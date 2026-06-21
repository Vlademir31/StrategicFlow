import asyncpg

class InventoryService:
    def __init__(self, request):
        self.request = request
        self.pool: asyncpg.pool.Pool = request.app["db"]

    async def list_inventory(self):
        tenant_id = self.request.headers.get("X-Tenant-ID", "default")

        query = """
            SELECT
                id,
                tenant_id,
                sku,
                sku_name,
                quantity_available,
                quantity_reserved,
                location,
                class_,
                last_updated
            FROM inventory
            WHERE tenant_id = $1
            ORDER BY sku
        """

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, tenant_id)

        return [dict(r) for r in rows]
