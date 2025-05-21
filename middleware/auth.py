import os
from dotenv import load_dotenv
load_dotenv()
import jwt
from fastapi import Request, HTTPException


class AuthMiddleware:
    def __init__(self):
        self.SECRET_KEY = os.getenv("TOKEN_KEY")

    def verify_request(self, request: Request):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            raise ValueError("Missing or invalid Authorization header")

        token = auth_header.split(" ")[1]
        verify_token(token)
        
        return 
    

def verify_token(token):
    try:
        secret = os.getenv("TOKEN_KEY")
        print(secret)
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload
    
    except jwt.ExpiredSignatureError:
        print("token expired")
        raise HTTPException(status_code=403, detail="Expired Token")
    
    except jwt.InvalidTokenError:
        print("token invalid")
        raise HTTPException(status_code=401, detail="Invlalid token")
    
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))