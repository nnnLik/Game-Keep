from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from conf.settings import settings


def get_uploads_dir() -> str:
    p = Path(__file__).resolve().parent.parent / settings.app.UPLOADS_DIR
    p.mkdir(parents=True, exist_ok=True)
    (p / 'avatars').mkdir(exist_ok=True)
    (p / 'banners').mkdir(exist_ok=True)
    return str(p)


def get_avatars_dir() -> str:
    return str(Path(get_uploads_dir()) / 'avatars')


def get_banners_dir() -> str:
    return str(Path(get_uploads_dir()) / 'banners')


def setup_static_files(app: FastAPI) -> None:
    app.mount('/uploads', StaticFiles(directory=get_uploads_dir()), name='uploads')
