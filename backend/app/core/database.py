from collections.abc import AsyncGenerator

from loguru import logger
from surrealdb import AsyncSurreal

from app.core.config import settings


def extract_records(result: object) -> list[dict]:
    """Extrai os registros do resultado de query do SurrealDB."""
    if not result:
        return []
    if isinstance(result, list):
        if len(result) > 0:
            if isinstance(result[0], list):
                return result[0]
            if isinstance(result[0], dict):
                if 'status' in result[0] and 'result' in result[0]:
                    res = result[0].get('result')
                    return res if isinstance(res, list) else [res] if res else []
                return result
    elif isinstance(result, dict):
        if 'status' in result and 'result' in result:
            res = result.get('result')
            return res if isinstance(res, list) else [res] if res else []
    return []


# Global persistent connection
db_client = AsyncSurreal(settings.SURREAL_URL)

async def init_db():
    logger.info("Conectando ao SurrealDB...")
    await db_client.connect()
    await db_client.signin({"username": settings.SURREAL_USER, "password": settings.SURREAL_PASS})
    await db_client.use(settings.SURREAL_NAMESPACE, settings.SURREAL_DATABASE)
    logger.info("SurrealDB conectado com sucesso")

async def close_db():
    await db_client.close()
    logger.info("SurrealDB desconectado")

async def get_db() -> AsyncSurreal:
    return db_client
