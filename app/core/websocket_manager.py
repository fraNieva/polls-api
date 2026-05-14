from typing import Dict, List
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Track active websocket connections per poll and broadcast updates."""

    def __init__(self):
        # Dictionary mapping poll_id to a list of active WebSocket connections
        # Example: { 1: [ws1, ws2], 2: [ws3] }
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, poll_id: int):
        """Accepts a new connection and adds it to the poll's listener list."""
        await websocket.accept()
        
        if poll_id not in self.active_connections:
            self.active_connections[poll_id] = []
        
        self.active_connections[poll_id].append(websocket)
        logger.info(
            "WebSocket connected to poll %s. Total listeners: %s",
            poll_id,
            len(self.active_connections[poll_id]),
        )

    def disconnect(self, websocket: WebSocket, poll_id: int):
        """Removes a connection from the listener list when a client disconnects."""
        if poll_id in self.active_connections:
            if websocket in self.active_connections[poll_id]:
                self.active_connections[poll_id].remove(websocket)
                
                # Cleanup: remove the poll key if no one is listening anymore
                if not self.active_connections[poll_id]:
                    del self.active_connections[poll_id]
        
        logger.info("WebSocket disconnected from poll %s", poll_id)

    async def broadcast_to_poll(self, poll_id: int, message: dict):
        """Sends a JSON message to all clients currently watching a specific poll."""
        if poll_id in self.active_connections:
            stale_connections: List[WebSocket] = []
            for connection in self.active_connections[poll_id]:
                try:
                    # send_json automatically serializes the dict to a JSON string
                    await connection.send_json(message)
                except Exception:
                    stale_connections.append(connection)
                    logger.exception(
                        "Failed to send websocket message to poll %s listener",
                        poll_id,
                    )

            for stale_connection in stale_connections:
                self.disconnect(stale_connection, poll_id)

# Global instance to be shared across endpoints
manager = ConnectionManager()
