import os
import jwt
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.testclient import TestClient 
from dotenv import load_dotenv
from middleware.auth import AuthMiddleware, verify_token
load_dotenv()

SECRET_KEY = os.getenv("TOKEN_KEY")
ALGORITHM = "HS256"

app = FastAPI()

app.add_middleware(AuthMiddleware)

@app.get("/test")
async def root():
    return {"message": "test"}



@app.websocket("/ws/{connection_id}")
async def websocket_endpoint(websocket: WebSocket, connection_id: str, token: str = Query(None)):
    await websocket.accept()
    try:
        payload = verify_token(f"Bearer {token}")
        
        print(f"WebSocket authenticated user: {payload}")
    except ValueError as e:
        await websocket.close(code=1008)  # Policy Violation
        print(f"WebSocket auth failed: {e}")
        return






# tests

def generate_token(payload: dict) -> str:
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    return token

def test_protected_route_with_valid_token():
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjE1LCJpYXQiOjE3NDY4MTUyMDQsImV4cCI6MTc0NzQyMDAwNH0.vYhVohwUh_fQldWkoM3BrtyoTKUKL7aju1pB8COAZ28"
    client = TestClient(app)

    response = client.get("/test", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    #assert response.json()["user"]["user_id"] == "123"

def test_protected_route_with_invalid_token():
    client = TestClient(app)
    response = client.get("/test", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"

def test_protected_route_without_token():
    client = TestClient(app)
    response = client.post("/test")
    assert response.status_code == 401
    assert response.json()["detail"] == "Missing or invalid Authorization header"

def test_websocket_with_valid_token():
    # Generate a valid token
    token = generate_token({"user_id": 123})
    
    # Create a TestClient instance
    client = TestClient(app)
    
    # Establish a WebSocket connection with the Authorization header
    with client.websocket_connect(f"/ws/connection_id?token={token}") as websocket:
        
        # Send a message (optional based on your WebSocket behavior)
        websocket.send_text("Hello WebSocket")
        
        # Receive a message (you can assert if the response is as expected)
        response = websocket.receive_text()
        assert response == "Expected response" 


