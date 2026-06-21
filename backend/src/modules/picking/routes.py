from aiohttp import web

def setup_picking_routes(app):
    app.router.add_get("/api/v1/picking", lambda r: web.json_response())
    print("OK picking")
