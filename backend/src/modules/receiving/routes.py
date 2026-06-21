from aiohttp import web
from .service import ReceivingService


async def list_receiving(request):
    service = ReceivingService(request)
    data = await service.list_receiving()
    return web.json_response(data)


def setup_receiving_routes(app):
    app.router.add_get("/api/v1/receiving", list_receiving)
    print("Receiving routes loaded")
