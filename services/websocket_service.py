from fastapi import WebSocket

class WebsocketService:
    def __init__(self, active_connections: dict[str, WebSocket]):
        self.active_connections = active_connections

    def add_connection(self, connection_id:str, websocket: WebSocket):
        self.active_connections[connection_id] = websocket
        print(f"connection {connection_id} added.")
        return
    
    def get_connection(self, connection_id: str) -> WebSocket:
        connection = self.active_connections.get(connection_id)
        if not connection:
            print(f"Connection {connection_id} not found in get_connection()")


        return connection

    async def close_connection(self, connection_id: str):
        if connection_id in self.active_connections:
            try:
                websocket = self.active_connections[connection_id]
                await websocket.close() 
                del self.active_connections[connection_id]  
                print(f'Connection: {connection_id} closed.')
                return
            except Exception as e:
                print(f"Error while closing connection {connection_id}: {e}")
                return
        else:
            print(f"Connection {connection_id} not found.")
            return
        