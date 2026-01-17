from fastapi import WebSocket

class ConnectionManager:
    """
    Manages active websocket connections.
    Think of this as the "Phone Book" of currently online users.
    """
    def __init__(self):
        # Dictionary to store {user_id: websocket_connection_object}
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept() # Accept the "phone call"
        self.active_connections[user_id] = websocket
        print(f"✅ User {user_id} connected.")

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            print(f"❌ User {user_id} disconnected.")

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            await websocket.send_text(message)