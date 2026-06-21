from aiohttp import web

def setup_inventory_routes(app):
    app.router.add_get("/api/v1/inventory", lambda r: web.json_response())
    print("OK inventory")
