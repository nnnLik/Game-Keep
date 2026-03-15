from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.auth import router as auth_router
from api.me import router as me_router
from api.user_games import router as user_games_router
from conf.settings import settings
from utils.static import setup_static_files


def build_app() -> FastAPI:
    app = FastAPI(title=settings.app.TITLE, version=settings.app.VERSION)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['http://localhost:3000', 'http://127.0.0.1:3000'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
    app.include_router(auth_router)
    app.include_router(me_router)
    app.include_router(user_games_router)
    setup_static_files(app)
    return app
