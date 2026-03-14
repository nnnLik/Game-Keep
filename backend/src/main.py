import uvicorn
from fastapi import FastAPI

from api.auth import router as auth_router
from conf.settings import settings

app = FastAPI(title=settings.app.TITLE, version=settings.app.VERSION)
app.include_router(auth_router)


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=settings.app.HOST,
        port=settings.app.PORT,
        reload=settings.app.RELOAD,
        log_level=settings.app.LOG_LEVEL,
    )
