from langchain_openai import ChatOpenAI
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, WebSocket
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from utils.link_card_parser import LinkCardParser
from services.files_service import FilesService
from config.database import get_db
from services.websocket_service import WebsocketService


app = FastAPI()
active_connections = {}
websocketService = WebsocketService(active_connections)


@app.post("/create", response_class=JSONResponse)
async def process_file(
    connection_id = str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
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
        files_service = FilesService()
        websocket = websocketService.get_connection(connection_id)
        parser = LinkCardParser(model, db, websocket)

        rows = files_service.parse_file(file.filename, content)
        results = await parser.convert_to_json(rows)

        return {
            "filename": file.filename,
            "success_count": len([row for row in results if "error" not in row]),
            "error_count": len([row for row in results if "error" in row]),
            "results": results
        }
    
    except Exception as e:
        print(e)
        raise HTTPException(500, "Unable to process request at this time") 
    

@app.websocket("/ws/{connection_id}")
async def websocket_endpoint(websocket: WebSocket, connection_id: str):
    await websocket.accept()   


