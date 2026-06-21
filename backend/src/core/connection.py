import asyncpg
import asyncio
import logging
from core.config import settings
from core.database import set_pool

logger = logging.getLogger("database")
logger.setLevel(logging.INFO)

async def _create_system_tables(pool):
    """Cria tabelas principais e injeta massa inicial"""
    async with pool.acquire() as conn:
        async with conn.transaction():
            # KPIs
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS kpis (
                    id SERIAL PRIMARY KEY,
                    tenant_id VARCHAR(50) NOT NULL,
                    name VARCHAR(50) NOT NULL,
                    value NUMERIC(12, 4) NOT NULL,
                    unit VARCHAR(10) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_kpis_tenant ON kpis(tenant_id);
            """)

            # Refresh tokens
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS security_refresh_tokens (
                    id SERIAL PRIMARY KEY,
                    tenant_id VARCHAR(50) NOT NULL,
                    user_id VARCHAR(255) NOT NULL,
                    token VARCHAR(500) NOT NULL,
                    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Roles
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS security_roles (
                    id SERIAL PRIMARY KEY,
                    tenant_id VARCHAR(50) NOT NULL,
                    name VARCHAR(50) NOT NULL,
                    permissions TEXT[] NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Seed KPIs
            await conn.execute("""
                INSERT INTO kpis (tenant_id, name, value, unit)
                SELECT 'default-tenant', 'cycleTime', 19.5, 'h'
                WHERE NOT EXISTS (SELECT 1 FROM kpis WHERE name = 'cycleTime');
            """)

            logger.info("[DB] Tabelas criadas e seed inicial aplicado.")

async def init_db(max_retries: int = 10, base_delay: float = 1.0):
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"[DB] Tentando conectar ao PostgreSQL (tentativa {attempt}/{max_retries})...")
            pool = await asyncpg.create_pool(dsn=settings.DB_URL)
            set_pool(pool)
            await _create_system_tables(pool)
            logger.info("[DB] Conexão estabelecida com sucesso!")
            return pool
        except Exception as e:
            wait_time = base_delay * (2 ** (attempt - 1))
            logger.error(f"[DB] Falha ao conectar: {e}")
            logger.info(f"[DB] Aguardando {wait_time:.1f}s antes de tentar novamente...")
            await asyncio.sleep(wait_time)
    logger.critical("[DB] Não foi possível conectar ao PostgreSQL após várias tentativas.")
    raise RuntimeError("Falha ao conectar ao banco de dados.")

async def close_db(pool):
    if pool:
        await pool.close()
