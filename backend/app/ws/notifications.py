import asyncio
import json
from collections import defaultdict
from typing import Optional

import redis.asyncio as aioredis
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from fastapi.websockets import WebSocketState

from app.core.config import settings
from app.core.security import decode_token
from app.core.redis import get_pubsub_pool

ws_router = APIRouter()


class ConnectionManager:
    def __init__(self):
        # Maps user_id -> set of active WebSocket connections
        self._connections: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, websocket: WebSocket, user_id: str) -> None:
        await websocket.accept()
        self._connections[user_id].add(websocket)

    def disconnect(self, user_id: str, websocket: WebSocket) -> None:
        self._connections[user_id].discard(websocket)
        if not self._connections[user_id]:
            del self._connections[user_id]

    async def send_to_user(self, user_id: str, data: dict) -> None:
        connections = self._connections.get(user_id, set()).copy()
        dead = set()
        for ws in connections:
            try:
                if ws.client_state == WebSocketState.CONNECTED:
                    await ws.send_json(data)
                else:
                    dead.add(ws)
            except Exception:
                dead.add(ws)
        for ws in dead:
            self._connections[user_id].discard(ws)

    async def broadcast(self, data: dict) -> None:
        for user_id in list(self._connections.keys()):
            await self.send_to_user(user_id, data)


manager = ConnectionManager()


async def _redis_listener(user_id: str, websocket: WebSocket) -> None:
    """Subscribe to Redis pub/sub and forward messages to the WebSocket."""
    redis_client: aioredis.Redis = get_pubsub_pool()
    pubsub = redis_client.pubsub()
    channel = f"notifications:{user_id}"

    await pubsub.subscribe(channel)
    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    payload = json.loads(message["data"])
                    if websocket.client_state == WebSocketState.CONNECTED:
                        await websocket.send_json(payload)
                    else:
                        break
                except Exception:
                    break
    except asyncio.CancelledError:
        pass
    finally:
        try:
            await pubsub.unsubscribe(channel)
            await pubsub.aclose()
        except Exception:
            pass


@ws_router.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket, token: Optional[str] = None):
    """WebSocket endpoint for real-time notifications.

    Connect with: ws://host/ws/notifications?token=<access_token>
    """
    if not token:
        await websocket.close(code=4001)
        return

    try:
        payload = decode_token(token)
        user_id: Optional[str] = payload.get("sub")
        if not user_id:
            await websocket.close(code=4001)
            return
    except Exception:
        await websocket.close(code=4001)
        return

    await manager.connect(websocket, user_id)

    listener_task = asyncio.create_task(_redis_listener(user_id, websocket))

    try:
        while True:
            # Keep connection alive; client can send pings
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30)
                if data == "ping":
                    await websocket.send_text("pong")
            except asyncio.TimeoutError:
                # Send ping to check connection is alive
                try:
                    await websocket.send_json({"type": "ping"})
                except Exception:
                    break
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        listener_task.cancel()
        manager.disconnect(user_id, websocket)
        try:
            await listener_task
        except asyncio.CancelledError:
            pass
