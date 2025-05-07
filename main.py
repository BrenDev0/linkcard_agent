from langchain_openai import ChatOpenAI
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from utils.link_card_parser import LinkCardParser
from services.files_service import FilesService
from config.database import get_db
from services.websocket_service import WebsocketService


app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://smart-cards-dups8l0ky-soul-lens.vercel.app/",
    "https://smart-cards-mu.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
)

active_connections = {}
websocketService = WebsocketService(active_connections)

@app.post("/api/parse-file", response_class=JSONResponse)
async def process_file(

    connection_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    
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

        websocket = websocketService.get_connection(connection_id)

        if websocket is None:
            raise HTTPException(status_code=404, detail="Websocket connection not found.")
        
        parser = LinkCardParser(model=model, db=db, websocket=websocket)

        files_service = FilesService()
        rows = files_service.parse_file(filename=file.filename, content=content)
        results = await parser.convert_to_json(rows)

        return {
            "filename": file.filename,
            "success_count": len([row for row in results if "error" not in row]),
            "error_count": len([row for row in results if "error" in row]),
            "results": results
        }
    
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Unable to process request at this time.") 
    

@app.websocket("/ws/{connection_id}")
async def websocket_endpoint(websocket: WebSocket, connection_id: str):
    await websocket.accept()
    websocketService.add_connection(connection_id, websocket)
    print(f'Websocket connection: {connection_id} opened.')
    try:
        while True: 
            await websocket.receive_text()

    except WebSocketDisconnect:
        await websocketService.close_connection(connection_id)
        print(f'Websocket connection: {connection_id} closed.')

