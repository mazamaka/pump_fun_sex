import asyncio
import json
from typing import Optional
import websockets

from config import settings
from .repository import TokenEventRepository
from loguru import logger
from .realtime import WSManager


class Ingestor:
    def __init__(self, repo: Optional[TokenEventRepository] = None, manager: Optional[WSManager] = None) -> None:
        self.repo = repo or TokenEventRepository()
        self.manager = manager
        self._task: Optional[asyncio.Task] = None
        self._stop = asyncio.Event()

    async def start(self) -> None:
        if self._task and not self._task.done():
            return
        self._stop.clear()
        logger.debug("ingestor_starting")
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        self._stop.set()
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _run(self) -> None:
        uri = settings.websocket_url
        backoff = 1
        while not self._stop.is_set():
            try:
                logger.debug("ws_connecting url={}", uri)
                async with websockets.connect(uri, ping_interval=20, ping_timeout=20) as ws:
                    await ws.send(json.dumps({"method": "subscribeNewToken"}))
                    logger.debug("ws_subscribed channel=subscribeNewToken")
                    backoff = 1
                    async for msg in ws:
                        data = json.loads(msg)
                        if not isinstance(data, dict):
                            continue
                        if "signature" not in data:
                            continue
                        pool = str(data.get("pool", "")).lower()
                        if pool != "pump":
                            continue
                        await asyncio.to_thread(self.repo.upsert_from_event, data)
                        logger.debug(
                            "event_ingested tx_type={} signature={} symbol={} mint={}",
                            data.get("txType"),
                            data.get("signature"),
                            data.get("symbol"),
                            data.get("mint"),
                        )
                        if self.manager:
                            payload = {
                                "type": "new_token",
                                "signature": data.get("signature"),
                                "txType": data.get("txType"),
                                "symbol": data.get("symbol"),
                                "name": data.get("name"),
                                "mint": data.get("mint"),
                                "marketCapSol": data.get("marketCapSol"),
                                "solAmount": data.get("solAmount"),
                                "initialBuy": data.get("initialBuy"),
                                "uri": data.get("uri"),
                                "pool": data.get("pool"),
                            }
                            await self.manager.broadcast(payload)
            except Exception:
                logger.exception("ingestor_error backoff={}s", backoff)
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 30)
