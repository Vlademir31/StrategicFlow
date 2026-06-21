from aiohttp import web
from .picking_service import PickingService

async def list_picking(request):
    service = PickingService(request)
    return web.json_response(await service.list_raw())

async def dashboard_picking(request):
    service = PickingService(request)
    return web.json_response(await service.dashboard())

def setup_picking_routes(app):
    app.router.add_get("/api/v1/picking", list_picking)
    app.router.add_get("/api/v1/picking/dashboard", dashboard_picking)
    print("OK picking consultivo")
