import os
from dotenv import load_dotenv
load_dotenv()
import jwt
from fastapi import Request, HTTPException


class AuthMiddleware:
    def __init__(self):
        self.SECRET_KEY = os.getenv("TOKEN_KEY")

    def get_auth_header(self, request: Request):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            raise ValueError("Missing or invalid Authorization header")
        
        return auth_header
    

    def verify_token(self, request_or_token):
        try:
            if isinstance(request_or_token, Request):
                auth_header = self.get_auth_header(request_or_token)
                token = auth_header.split(" ")[1]
            elif isinstance(request_or_token, str):
                if not request_or_token.startswith("Bearer "):
                    raise ValueError("Token must start with 'Bearer '")
                token = request_or_token.split(" ")[1]
            else:
                raise ValueError("Invalid input type for verify_token")

            payload = jwt.decode(token, self.SECRET_KEY, algorithms=["HS256"])
            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=403, detail="Expired Token")

        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid Token")

        except ValueError as e:
            raise HTTPException(status_code=401, detail=str(e))
