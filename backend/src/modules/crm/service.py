from core.database import get_db
from .schemas import CompanySchema, OpportunitySchema

async def get_companies(tenant_id: str) -> list[dict]:
    db = await get_db()
    rows = await db.fetch("SELECT * FROM crm_companies WHERE tenant_id = $1 ORDER BY razao_social", tenant_id)
    return [dict(row) for row in rows]

async def create_company(data: dict, tenant_id: str) -> dict:
    schema = CompanySchema(**data)
    db = await get_db()
    query = """
        INSERT INTO crm_companies (tenant_id, razao_social, cnpj, segmento, porte_empresa, numero_funcionarios)
        VALUES ($1, $2, $3, $4, $5, $6) RETURNING *;
    """
    row = await db.fetchrow(query, tenant_id, schema.razao_social, schema.cnpj, schema.segmento, schema.porte_empresa, schema.numero_funcionarios)
    return dict(row)

async def get_opportunities(tenant_id: str) -> list[dict]:
    db = await get_db()
    query = """
        SELECT o.*, c.razao_social 
        FROM crm_opportunities o
        JOIN crm_companies c ON o.id_empresa = c.id_empresa
        WHERE o.tenant_id = $1 
        ORDER BY o.valor_projeto DESC;
    """
    rows = await db.fetch(query, tenant_id)
    return [dict(row) for row in rows]
