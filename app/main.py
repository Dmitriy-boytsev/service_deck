from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from app.core.config import settings
from app.api.v1.endpoints.endpoints import router
from app.core.db.init_db import init_models
from app.api.v1.handlers.email_handler import check_emails_periodically

import logging
logger = logging.getLogger(__name__)


app = FastAPI(
    title=settings.app_title,
    description=settings.description,
    version=settings.version,
)


origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router, prefix="/api/v1/tickets", tags=["Tickets"])


@app.on_event("startup")
async def on_startup():
    """Запуск обработчика почты при старте приложения"""
    logger.info("Периодическая проверка почты запущена")
    asyncio.create_task(check_emails_periodically())


@app.get("/")
def root():
    return {"message": "Добро пожаловать в ServiceDesk API"}


if __name__ == "__main__":
    asyncio.run(init_models())
    asyncio.run(on_startup())