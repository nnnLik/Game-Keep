import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.auth import router as auth_router
from conf.settings import settings

app = FastAPI(title=settings.app.TITLE, version=settings.app.VERSION)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000', 'http://127.0.0.1:3000'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.include_router(auth_router)


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=settings.app.HOST,
        port=settings.app.PORT,
        reload=settings.app.RELOAD,
        log_level=settings.app.LOG_LEVEL,
    )
