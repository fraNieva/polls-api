import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websocket_manager import manager

router = APIRouter()

logger = logging.getLogger(__name__)

@router.websocket("/ws/polls/{poll_id}")
async def websocket_endpoint(websocket: WebSocket, poll_id: int):
    """Keep a poll-specific websocket connection alive and clean up on disconnect."""
    # Step 1 & 2: Connect and register the listener
    await manager.connect(websocket, poll_id)
    
    try:
        while True:
            # We don't expect messages FROM the client in this app (voting is via POST),
            # but we must listen for data or pings to keep the connection alive
            # and detect when the client closes the browser.
            await websocket.receive_text()
    except WebSocketDisconnect:
        # Step 4: Cleanup on disconnection
        manager.disconnect(websocket, poll_id)
    except Exception:
        # Handle unexpected errors gracefully
        logger.exception("WebSocket error on poll %s", poll_id)
        manager.disconnect(websocket, poll_id)
