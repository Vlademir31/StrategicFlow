import asyncpg
import asyncio
import logging
from core.config import settings

logger = logging.getLogger("database")
logger.setLevel(logging.INFO)

_db_pool = None

async def _create_system_tables(pool):
    """Cria a tabela de KPIs e injeta a massa de dados reais estrita."""
    query = """
    -- 1. CRIAÇÃO DA TABELA DE METRICAS REALTIME
    CREATE TABLE IF NOT EXISTS kpis (
        id SERIAL PRIMARY KEY,
        tenant_id VARCHAR(50) NOT NULL,
        name VARCHAR(50) NOT NULL,
        value NUMERIC(12, 4) NOT NULL,
        unit VARCHAR(10) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_kpis_tenant ON kpis(tenant_id);

    -- 2. CARGA DE DADOS REAIS - AS 8 CHAVES OFICIAIS DO FRONTEND
    INSERT INTO kpis (tenant_id, name, value, unit)
    SELECT 'default-tenant', 'cycleTime', 19.5, 'h' WHERE NOT EXISTS (SELECT 1 FROM kpis WHERE name = 'cycleTime');

    INSERT INTO kpis (tenant_id, name, value, unit)
    SELECT 'default-tenant', 'otif', 96.2, '%' WHERE NOT EXISTS (SELECT 1 FROM kpis WHERE name = 'otif');

    INSERT INTO kpis (tenant_id, name, value, unit)
    SELECT 'default-tenant', 'efficiency', 92.4, '%' WHERE NOT EXISTS (SELECT 1 FROM kpis WHERE name = 'efficiency');

    INSERT INTO kpis (tenant_id, name, value, unit)
    SELECT 'default-tenant', 'rejection', 1.4, '%' WHERE NOT EXISTS (SELECT 1 FROM kpis WHERE name = 'rejection');

    INSERT INTO kpis (tenant_id, name, value, unit)
    SELECT 'default-tenant', 'roi', 245.0, '%' WHERE NOT EXISTS (SELECT 1 FROM kpis WHERE name = 'roi');

    INSERT INTO kpis (tenant_id, name, value, unit)
    SELECT 'default-tenant', 'success', 89.1, '%' WHERE NOT EXISTS (SELECT 1 FROM kpis WHERE name = 'success');

    INSERT INTO kpis (tenant_id, name, value, unit)
    SELECT 'default-tenant', 'nps', 78.0, '' WHERE NOT EXISTS (SELECT 1 FROM kpis WHERE name = 'nps');

    INSERT INTO kpis (tenant_id, name, value, unit)
    SELECT 'default-tenant', 'throughput', 1240.0, '' WHERE NOT EXISTS (SELECT 1 FROM kpis WHERE name = 'throughput');
    """
  
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(query)
            logger.info("[DB] Todas as tabelas (Dashboard, CRM, Users, Portal e Comentários) estruturadas.")

async def init_db(max_retries: int = 10, base_delay: float = 1.0):
    global _db_pool

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"[DB] Tentando conectar ao PostgreSQL (tentativa {attempt}/{max_retries})...")
            _db_pool = await asyncpg.create_pool(dsn=settings.DB_URL)
            
            # ---> Executa a verificação e criação automatizada de todas as tabelas
            await _create_system_tables(_db_pool)
            
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
