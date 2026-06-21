from core.database import get_db
from datetime import datetime

async def create_template(data: dict, tenant_id: str):
    db = await get_db()
    row = await db.fetchrow("""
        INSERT INTO templates (tenant_id, name, category, description, content, created_at, updated_at)
        VALUES ($1, $2, $3, $4, $5, $6, $6)
        RETURNING id, tenant_id, name, category, description, content, created_at, updated_at
    """, tenant_id, data["name"], data["category"], data.get("description"), data["content"], datetime.now())
    return dict(row)

async def list_templates(tenant_id: str):
    db = await get_db()
    rows = await db.fetch("SELECT * FROM templates WHERE tenant_id=$1 ORDER BY updated_at DESC", tenant_id)
    return [dict(r) for r in rows]

async def get_template_by_id(template_id: int, tenant_id: str):
    db = await get_db()
    row = await db.fetchrow("SELECT * FROM templates WHERE id=$1 AND tenant_id=$2", template_id, tenant_id)
    return dict(row) if row else None
