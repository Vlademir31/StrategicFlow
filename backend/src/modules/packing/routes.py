from aiohttp import web
from .packing_service import PackingService

async def list_packing(request):
    service = PackingService(request)
    return web.json_response(await service.list_raw())

async def dashboard_packing(request):
    service = PackingService(request)
    return web.json_response(await service.dashboard())

def setup_packing_routes(app):
    app.router.add_get("/api/v1/packing", list_packing)
    app.router.add_get("/api/v1/packing/dashboard", dashboard_packing)
    print("OK packing consultivo")
