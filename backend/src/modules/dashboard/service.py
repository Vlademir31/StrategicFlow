from core.database import get_db
from .models import Kpi

async def get_kpis(tenant_id: str) -> list[Kpi]:
    db = await get_db()
    rows = await db.fetch(
        """
        SELECT name, value, unit, tenant_id
        FROM kpis
        WHERE tenant_id = $1
        """,
        tenant_id,
    )
    return [
        Kpi(
            name=r["name"], 
            value=float(r["value"]), 
            unit=r["unit"], 
            tenant_id=r["tenant_id"]
        ) 
        for r in rows
    ]
