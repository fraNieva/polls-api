"""WebSocket tests for connection lifecycle and poll-scoped broadcasting."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import WebSocketDisconnect
from fastapi.testclient import TestClient

from app.api.v1.endpoints.websocket import websocket_endpoint
from app.core.websocket_manager import ConnectionManager, manager
from main import app


class TestConnectionManager:
    """Unit tests for connection registration, cleanup, and broadcast behavior."""

    @pytest.mark.asyncio
    async def test_connect_registers_socket_under_poll(self) -> None:
        connection_manager = ConnectionManager()
        websocket = AsyncMock()

        await connection_manager.connect(websocket, poll_id=10)

        websocket.accept.assert_awaited_once()
        assert 10 in connection_manager.active_connections
        assert websocket in connection_manager.active_connections[10]

    @pytest.mark.asyncio
    async def test_disconnect_removes_poll_key_when_empty(self) -> None:
        connection_manager = ConnectionManager()
        websocket = AsyncMock()

        connection_manager.active_connections[20] = [websocket]
        connection_manager.disconnect(websocket, poll_id=20)

        assert 20 not in connection_manager.active_connections

    @pytest.mark.asyncio
    async def test_broadcast_sends_message_to_all_connections(self) -> None:
        connection_manager = ConnectionManager()
        ws1 = AsyncMock()
        ws2 = AsyncMock()
        message: dict[str, Any] = {'type': 'vote_update', 'data': {'id': 1}}

        connection_manager.active_connections[30] = [ws1, ws2]
        await connection_manager.broadcast_to_poll(30, message)

        ws1.send_json.assert_awaited_once_with(message)
        ws2.send_json.assert_awaited_once_with(message)

    @pytest.mark.asyncio
    async def test_broadcast_removes_stale_connections(self) -> None:
        connection_manager = ConnectionManager()
        stale_ws = AsyncMock()
        healthy_ws = AsyncMock()
        stale_ws.send_json.side_effect = RuntimeError('socket is closed')
        message: dict[str, Any] = {'type': 'vote_update', 'data': {'id': 2}}

        connection_manager.active_connections[40] = [stale_ws, healthy_ws]
        await connection_manager.broadcast_to_poll(40, message)

        healthy_ws.send_json.assert_awaited_once_with(message)
        assert stale_ws not in connection_manager.active_connections[40]


class TestWebSocketEndpoint:
    """Integration tests for /api/v1/ws/polls/{poll_id}."""

    def test_websocket_endpoint_accepts_connection(self) -> None:
        with TestClient(app) as client:
            with client.websocket_connect('/api/v1/ws/polls/55') as websocket:
                websocket.send_text('ping')

        # Connection should be cleaned up after context manager exits.
        assert 55 not in manager.active_connections

    def test_websocket_broadcast_reaches_connected_client(self) -> None:
        import anyio

        with TestClient(app) as client:
            with client.websocket_connect('/api/v1/ws/polls/77') as websocket:
                payload = {'type': 'vote_update', 'data': {'id': 77, 'total_votes': 3}}
                websocket.send_text('keepalive')

                # Run async broadcast from sync test through AnyIO in TestClient context.
                anyio.run(manager.broadcast_to_poll, 77, payload)
                received = websocket.receive_json()

                assert received == payload

        assert 77 not in manager.active_connections

    @pytest.mark.asyncio
    async def test_websocket_endpoint_disconnect_calls_manager_disconnect(self) -> None:
        websocket = AsyncMock()
        websocket.receive_text.side_effect = WebSocketDisconnect()

        original_connect = manager.connect
        original_disconnect = manager.disconnect

        mocked_connect = AsyncMock()
        mocked_disconnect = MagicMock()
        manager.connect = mocked_connect
        manager.disconnect = mocked_disconnect

        try:
            await websocket_endpoint(websocket, poll_id=88)

            mocked_connect.assert_awaited_once_with(websocket, 88)
            mocked_disconnect.assert_called_once_with(websocket, 88)
        finally:
            manager.connect = original_connect
            manager.disconnect = original_disconnect
