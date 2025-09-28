from __future__ import annotations

from typing import Set

from fastapi import WebSocket
from loguru import logger


class WSManager:
    def __init__(self) -> None:
        self._connections: Set[WebSocket] = set()

    async def connect(self, ws: WebSocket, accept: bool = True) -> None:
        if accept:
            await ws.accept()
        self._connections.add(ws)
        logger.info("ws_client_connected total={} ", len(self._connections))

    async def disconnect(self, ws: WebSocket) -> None:
        try:
            self._connections.remove(ws)
        except KeyError:
            pass
        logger.info("ws_client_disconnected total={}", len(self._connections))

    async def broadcast(self, message: dict) -> None:
        total = len(self._connections)
        logger.info(
            "ws_broadcast recipients={} type={} signature={}",
            total,
            message.get("type"),
            message.get("signature"),
        )
        dead = []
        for ws in list(self._connections):
            try:
                await ws.send_json(message)
            except Exception:
                logger.exception("ws_send_failed")
                dead.append(ws)
        for ws in dead:
            await self.disconnect(ws)
