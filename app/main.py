from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from .admin import setup_admin
from .db import init_db
from .ingestor import Ingestor
from .routes.tokens import router as tokens_router
from .routes.ws import router as ws_router
from .realtime import WSManager
from .core.logging import setup_logging


def create_app() -> FastAPI:
    app = FastAPI(title="PumpFun Tracker")

    setup_logging("INFO")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.mount("/static", StaticFiles(directory="app/admin/static"), name="static")

    app.include_router(tokens_router)
    app.include_router(ws_router)
    setup_admin(app)

    @app.get("/")
    def root():
        return {
            "name": "pumpfun-tracker",
            "docs": "/docs",
            "redoc": "/redoc",
            "admin": "/admin",
            "tokens": "/tokens",
            "health": "/healthz",
        }

    @app.get("/healthz")
    async def health():
        return {"status": "ok"}

    @app.on_event("startup")
    async def on_startup():
        init_db()
        app.state.ws_manager = WSManager()
        app.state.ingestor = Ingestor(manager=app.state.ws_manager)
        await app.state.ingestor.start()

    @app.on_event("shutdown")
    async def on_shutdown():
        ingestor = getattr(app.state, "ingestor", None)
        if ingestor:
            await ingestor.stop()

    return app


app = create_app()
