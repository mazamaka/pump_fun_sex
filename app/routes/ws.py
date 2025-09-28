from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from loguru import logger

from ..realtime import WSManager

router = APIRouter()


def get_manager(websocket: WebSocket) -> WSManager:
    return websocket.app.state.ws_manager


@router.websocket("/ws/tokens")
async def ws_tokens(websocket: WebSocket, manager: WSManager = Depends(get_manager)):
    await manager.connect(websocket)
    logger.info("ws_tokens_connected")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        logger.info("ws_tokens_disconnected")
        await manager.disconnect(websocket)
    except Exception:
        logger.exception("ws_tokens_error")
        await manager.disconnect(websocket)
