from aiohttp import web

def setup_receiving_routes(app):
    app.router.add_get("/api/v1/receiving", lambda r: web.json_response())
    print("OK receiving")
