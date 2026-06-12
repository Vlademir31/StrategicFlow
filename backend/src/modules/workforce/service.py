from core.database import get_db
from .schemas import ConsultantSchema

async def get_consultants_dashboard(tenant_id: str) -> list[dict]:
    """Busca a lista de consultores calculando em tempo real a Taxa de Utilização (Billable Hours)."""
    db = await get_db()
    query = """
        SELECT 
            c.id_consultor,
            c.nome,
            c.cargo_senioridade,
            c.hard_skills,
            c.custo_hora::float,
            COALESCE(a.status_disponibilidade, 'Disponível') as status,
            COALESCE(a.porcentagem_dedicacao, 0) as dedicacao_atual,
            -- Cálculo da Taxa de Utilização Vital para Consultorias (Faturamento vs Capacidade)
            ROUND(
                (COALESCE(a.horas_faturadas_mes, 0)::numeric / c.horas_uteis_mes::numeric) * 100, 1
            )::float as taxa_utilizacao_percent
        FROM workforce_consultants c
        LEFT JOIN workforce_allocations a ON c.id_consultor = a.id_consultor
        WHERE c.tenant_id = $1 AND c.status_consultor = 'Ativo'
        ORDER BY taxa_utilizacao_percent DESC;
    """
    rows = await db.fetch(query, tenant_id)
    return [dict(row) for row in rows]

async def create_consultant(data: dict, tenant_id: str) -> dict:
    schema = ConsultantSchema(**data)
    db = await get_db()
    query = """
        INSERT INTO workforce_consultants (tenant_id, nome, cargo_senioridade, hard_skills, background_setorial, custo_hora, horas_uteis_mes)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING id_consultor, nome, cargo_senioridade, custo_hora::float;
    """
    row = await db.fetchrow(
        query, tenant_id, schema.nome, schema.cargo_senioridade, 
        schema.hard_skills, schema.background_setorial, schema.custo_hora, schema.horas_uteis_mes
    )
    return dict(row)
