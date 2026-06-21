import asyncpg
from typing import List, Dict, Any


class ReceivingService:
    def __init__(self, request):
        self.request = request
        self.pool: asyncpg.pool.Pool = request.app["db"]

    async def list_receiving(self) -> List[Dict[str, Any]]:
        tenant_id = self.request.headers.get("X-Tenant-ID", "default")

        query = """
            SELECT
                id,
                tenant_id,
                nf_number,
                sku,
                quantity_expected,
                quantity_received,
                status,
                cycle_time_hours,
                operator_name,
                created_at
            FROM receiving
            WHERE tenant_id = $1
            ORDER BY created_at DESC
        """

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, tenant_id)

        return [dict(r) for r in rows]
