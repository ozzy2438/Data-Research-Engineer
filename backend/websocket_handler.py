"""
WebSocket Handler for Real-time Updates
Handles real-time communication for research progress and PDF processing
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import asyncio
import uuid

class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.job_connections: Dict[str, List[str]] = {}  # job_id -> [connection_ids]
    
    async def connect(self, websocket: WebSocket) -> str:
        """Accept new WebSocket connection"""
        await websocket.accept()
        connection_id = str(uuid.uuid4())
        self.active_connections[connection_id] = websocket
        return connection_id
    
    def disconnect(self, connection_id: str):
        """Remove connection"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        # Remove from job connections
        for job_id, conn_ids in self.job_connections.items():
            if connection_id in conn_ids:
                conn_ids.remove(connection_id)
    
    def subscribe_to_job(self, connection_id: str, job_id: str):
        """Subscribe connection to job updates"""
        if job_id not in self.job_connections:
            self.job_connections[job_id] = []
        
        if connection_id not in self.job_connections[job_id]:
            self.job_connections[job_id].append(connection_id)
    
    async def send_personal_message(self, message: dict, connection_id: str):
        """Send message to specific connection"""
        if connection_id in self.active_connections:
            try:
                websocket = self.active_connections[connection_id]
                await websocket.send_text(json.dumps(message))
            except:
                self.disconnect(connection_id)
    
    async def send_job_update(self, job_id: str, update: dict):
        """Send update to all connections following a job"""
        if job_id in self.job_connections:
            message = {
                "type": "job_update",
                "job_id": job_id,
                **update
            }
            
            disconnected = []
            for connection_id in self.job_connections[job_id]:
                try:
                    if connection_id in self.active_connections:
                        websocket = self.active_connections[connection_id]
                        await websocket.send_text(json.dumps(message))
                    else:
                        disconnected.append(connection_id)
                except:
                    disconnected.append(connection_id)
            
            # Clean up disconnected connections
            for conn_id in disconnected:
                self.disconnect(conn_id)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connections"""
        disconnected = []
        for connection_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message))
            except:
                disconnected.append(connection_id)
        
        # Clean up disconnected connections
        for conn_id in disconnected:
            self.disconnect(conn_id)

# Global connection manager
manager = ConnectionManager()

class ResearchProgressTracker:
    """Tracks and broadcasts research progress"""
    
    @staticmethod
    async def update_progress(job_id: str, progress: int, message: str, extra_data: dict = None):
        """Update job progress and broadcast to subscribers"""
        update = {
            "progress": progress,
            "message": message,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        if extra_data:
            update.update(extra_data)
        
        await manager.send_job_update(job_id, update)
    
    @staticmethod
    async def notify_pdfs_found(job_id: str, pdfs: List[dict]):
        """Notify that PDFs have been found"""
        await manager.send_job_update(job_id, {
            "event": "pdfs_found",
            "found_pdfs": pdfs,
            "count": len(pdfs)
        })
    
    @staticmethod
    async def notify_pdf_processing(job_id: str, pdf_index: int, pdf_title: str, progress: int):
        """Notify about PDF processing progress"""
        await manager.send_job_update(job_id, {
            "event": "pdf_processing",
            "pdf_index": pdf_index,
            "pdf_title": pdf_title,
            "pdf_progress": progress
        })
    
    @staticmethod
    async def notify_completion(job_id: str, results: dict):
        """Notify about job completion"""
        await manager.send_job_update(job_id, {
            "event": "completed",
            "results": results
        })
    
    @staticmethod
    async def notify_error(job_id: str, error: str):
        """Notify about job error"""
        await manager.send_job_update(job_id, {
            "event": "error",
            "error": error
        })

async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    connection_id = await manager.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "subscribe_job":
                job_id = message.get("job_id")
                if job_id:
                    manager.subscribe_to_job(connection_id, job_id)
                    await manager.send_personal_message({
                        "type": "subscribed",
                        "job_id": job_id
                    }, connection_id)
            
            elif message.get("type") == "ping":
                await manager.send_personal_message({
                    "type": "pong"
                }, connection_id)
    
    except WebSocketDisconnect:
        manager.disconnect(connection_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(connection_id) 