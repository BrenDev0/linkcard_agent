import os
from dotenv import load_dotenv
load_dotenv()
import jwt
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

SECRET_KEY = os.getenv("TOKEN_KEY")

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("Authorization")

        try:
            payload = verify_token(auth_header=auth_header)
            request.state.user = payload
        except ValueError as e:
            return JSONResponse(status_code=401, content={"detail": str(e)})

        return await call_next(request)
    

def verify_token(auth_header: str):
    if not auth_header or not auth_header.startswith("Bearer "):
        raise ValueError("Missing or invalid Authorization header")

    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        print("token expired")
        raise ValueError("Token has expired")
    
    except jwt.InvalidTokenError:
        print("token invalid")
        raise ValueError("Invalid token")
