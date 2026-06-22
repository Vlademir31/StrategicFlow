from aiohttp import web
from .shipping_service import ShippingService

async def list_shipping(request):
    service = ShippingService(request)
    return web.json_response(await service.list_raw())

async def dashboard_shipping(request):
    service = ShippingService(request)
    return web.json_response(await service.dashboard())

def setup_shipping_routes(app):
    app.router.add_get("/api/v1/shipping", list_shipping)
    app.router.add_get("/api/v1/shipping/dashboard", dashboard_shipping)
    print("OK shipping consultivo")
