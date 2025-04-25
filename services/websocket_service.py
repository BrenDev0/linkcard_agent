from fastapi import WebSocket, WebSocketDisconnect;
import json
from services.redis_service import RedisService

class WebsocketService:
    def __init__(self, active_connections: dict[str, WebSocket]):
        self.active_connections = active_connections

    def add_connection(self, connection_id:str, websocket: WebSocket):
        self.active_connections[connection_id] = websocket
        return
    
    def get_connection(self, connection_id: str) -> WebSocket:
        connection = self.active_connections.get(connection_id)

        return connection

    def close_connection(self, connection_id):
        self.active_connections.remove(connection_id)
        
        print(f'Connection: {connection_id} closed.')
        
        return
        