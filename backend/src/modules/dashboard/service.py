from core.database import get_db

async def get_kpis(tenant_id: str | None):
    db = await get_db()
    rows = await db.fetch(
        """
        SELECT name, value, unit
        FROM kpis
        WHERE tenant_id = $1
        """,
        tenant_id or "default-tenant",
    )
    return [dict(r) for r in rows]
