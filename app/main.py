from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from routes import files
from dependencies.websocket import websocketInstance
from middleware.auth import AuthMiddleware
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

app.add_middleware(AuthMiddleware)

app.include_router(files.router)

@app.get("/test")
async def root():
    return {"message": "test"}



@app.websocket("/ws/{connection_id}")
async def websocket_endpoint(websocket: WebSocket, connection_id: str):
    await websocket.accept()

    # auth
    token = websocket.headers.get("Authorization")

    try:
        payload = verify_token(token)
        
        print(f"WebSocket authenticated user: {payload}")
    except ValueError as e:
        await websocket.close(code=1008)  # Policy Violation
        print(f"WebSocket auth failed: {e}")
        return

    websocketInstance.add_connection(connection_id, websocket)
    
    print(f'Websocket connection: {connection_id} opened.')
    try:
        while True: 
            await websocket.receive_text()

    except WebSocketDisconnect:
        await websocketInstance.close_connection(connection_id)
        print(f'Websocket connection: {connection_id} closed.')

