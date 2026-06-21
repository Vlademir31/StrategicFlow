from aiohttp import web
from .service import InventoryService


async def list_inventory(request):
    service = InventoryService(request)
    data = await service.list_inventory()
    return web.json_response(data)


async def inventory_dashboard(request):
    service = InventoryService(request)
    data = await service.inventory_dashboard()
    return web.json_response(data)


async def create_inventory(request):
    service = InventoryService(request)
    data = await service.create_inventory()
    return web.json_response(data)


async def import_inventory(request):
    service = InventoryService(request)
    data = await service.import_inventory_csv()
    return web.json_response(data)


def setup_inventory_routes(app):
    app.router.add_get("/api/v1/inventory", list_inventory)                  # lista operacional
    app.router.add_get("/api/v1/inventory/dashboard", inventory_dashboard)   # visão consultiva
    app.router.add_post("/api/v1/inventory", create_inventory)               # cadastro manual
    app.router.add_post("/api/v1/inventory/import", import_inventory)        # importação CSV

    print("Inventory routes loaded (operational + consultive + create + import)")
