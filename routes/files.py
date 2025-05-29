from dotenv import load_dotenv
load_dotenv()
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from services.files_service import FilesService
from database.database import get_db
from langchain_openai import ChatOpenAI
from services.prompted_data_parser import PromptedDataParser
from dependencies.websocket import websocketInstance
from middleware.auth import AuthMiddleware

router = APIRouter(
    prefix="/api/files",
    tags=["files"],
)
auth = AuthMiddleware()
@router.post("/parse-file", response_class=JSONResponse)
async def process_file(
    backgroundTasks: BackgroundTasks,
    connection_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: None = Depends(auth.verify_request)
):
    try:
        if not file.filename.endswith((".csv", ".xlsx", ".xls")):
            raise HTTPException(400, "File must be csv, xlsx, or xls")
        
        content = await file.read()
        model = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2
        )

        websocket = websocketInstance.get_connection(connection_id)

        if websocket is None:
            raise HTTPException(status_code=404, detail="Websocket connection not found.")
        
        parser = PromptedDataParser(model=model, db=db, websocket=websocket)

        files_service = FilesService()
        rows = files_service.parse_file(filename=file.filename, content=content)
        data_to_parser = files_service.convert_rows_to_dict(rows)
        
        backgroundTasks.add_task(parser.convert_to_json, data_to_parser)
        backgroundTasks.add_task(websocketInstance.remove_connection, connection_id)

        return JSONResponse(status_code=200, content={"message": "File parsing in progress."});
    
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Unable to process request at this time.") 
    

    