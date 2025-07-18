"""
WebSocket Connection Manager
Real-time updates for the data engineering application
"""

from typing import List
from fastapi import WebSocket
import json
import asyncio

class ConnectionManager:
    """WebSocket connection manager"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Close WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific WebSocket"""
        try:
            await websocket.send_text(json.dumps(message))
        except:
            # Remove connection if it's broken
            self.disconnect(websocket)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected WebSockets"""
        if not self.active_connections:
            return
        
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                # Connection is broken, add to disconnected list
                disconnected.append(connection)
        
        # Clean up broken connections
        for connection in disconnected:
            self.disconnect(connection)
    
    async def send_status_update(self, status: str, message: str = None):
        """Send status update message"""
        update = {
            'type': 'status_update',
            'status': status,
            'timestamp': asyncio.get_event_loop().time()
        }
        
        if message:
            update['message'] = message
        
        await self.broadcast(update)
    
    def get_connection_count(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections) 