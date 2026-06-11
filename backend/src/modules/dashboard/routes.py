from aiohttp import web
from .service import get_kpis


def setup_dashboard_routes(app: web.Application):
    app.router.add_get("/api/kpis", kpis_handler)


async def kpis_handler(request: web.Request):
    tenant_id = request.get("tenant_id")
    data = await get_kpis(tenant_id)
    return web.json_response({"kpis": data})
