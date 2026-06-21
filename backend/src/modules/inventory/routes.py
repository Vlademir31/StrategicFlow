from aiohttp import web
from .service import InventoryService

async def list_inventory(request):
    service = InventoryService(request)
    data = await service.list_inventory()
    return web.json_response(data)

def setup_inventory_routes(app):
    app.router.add_get("/api/v1/inventory", list_inventory)
    print("Inventory routes loaded")
