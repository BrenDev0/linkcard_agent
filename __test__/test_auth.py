import os
import jwt
from fastapi.testclient import TestClient
from app.main import app 
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.getenv("TOKEN_KEY")
ALGORITHM = "HS256"

def generate_token(payload: dict) -> str:
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    print(f"TOKEN:::::: {token}")
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
