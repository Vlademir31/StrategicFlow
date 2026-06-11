import asyncpg
import asyncio
import logging
from core.config import settings

logger = logging.getLogger("database")
logger.setLevel(logging.INFO)

_db_pool = None

async def init_db(max_retries: int = 10, base_delay: float = 1.0):
    global _db_pool

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"[DB] Tentando conectar ao PostgreSQL (tentativa {attempt}/{max_retries})...")
            _db_pool = await asyncpg.create_pool(dsn=settings.DB_URL)
            logger.info("[DB] Conexão estabelecida com sucesso!")
            return _db_pool

        except Exception as e:
            wait_time = base_delay * (2 ** (attempt - 1))
            logger.error(f"[DB] Falha ao conectar: {e}")
            logger.info(f"[DB] Aguardando {wait_time:.1f}s antes de tentar novamente...")
            await asyncio.sleep(wait_time)

    logger.critical("[DB] Não foi possível conectar ao PostgreSQL após várias tentativas.")
    raise RuntimeError("Falha ao conectar ao banco de dados.")

async def get_db():
    global _db_pool
    if _db_pool is None:
        await init_db()
    return _db_pool