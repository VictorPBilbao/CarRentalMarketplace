from collections.abc import AsyncGenerator

from loguru import logger
from surrealdb import AsyncSurreal

from app.core.config import settings


async def get_db() -> AsyncGenerator[AsyncSurreal, None]:
    async with AsyncSurreal(settings.SURREAL_URL) as db:
        await db.signin({"username": settings.SURREAL_USER, "password": settings.SURREAL_PASS})
        await db.use(settings.SURREAL_NAMESPACE, settings.SURREAL_DATABASE)
        logger.debug("SurrealDB conectado")
        try:
            yield db
        finally:
            logger.debug("SurrealDB desconectado")
