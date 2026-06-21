# putaway_routes.py
from aiohttp import web
from .putaway_service import PutawayService

async def list_putaway(request):
    service = PutawayService(request)
    data = await service.list_raw()
    return web.json_response(data)

async def dashboard_putaway(request):
    service = PutawayService(request)
    data = await service.dashboard()
    return web.json_response(data)

def setup_putaway_routes(app):
    app.router.add_get("/api/v1/putaway", list_putaway)
    app.router.add_get("/api/v1/putaway/dashboard", dashboard_putaway)
    print("Putaway consultivo routes loaded")
