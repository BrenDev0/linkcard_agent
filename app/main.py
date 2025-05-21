from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from routes import files
from dependencies.websocket import websocketInstance
from middleware.auth import verify_token



app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://smart-cards-mu.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
)


app.include_router(files.router)


@app.websocket("/ws/{connection_id}")
async def websocket_endpoint(websocket: WebSocket, connection_id: str, token: str = Query(None)):   
    # auth
    try:
        payload = verify_token(token)
        
        print(f"WebSocket authenticated user: {payload}")
    except ValueError as e:
        print(f"WebSocket auth failed: {e}")
        return

    await websocket.accept()
    websocketInstance.add_connection(connection_id, websocket)
    
    print(f'Websocket connection: {connection_id} opened.')
    try:
        while True: 
            await websocket.receive_text()

    except WebSocketDisconnect:
        websocketInstance.remove_connection(connection_id)
        print(f'Websocket connection: {connection_id} closed.')

