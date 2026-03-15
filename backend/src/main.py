import uvicorn

from conf.settings import settings
from utils.app import build_app

app = build_app()

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=settings.app.HOST,
        port=settings.app.PORT,
        reload=settings.app.RELOAD,
        log_level=settings.app.LOG_LEVEL,
    )
