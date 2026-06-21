from aiohttp import web

def setup_lean_routes(app):
    app.router.add_get("/api/v1/lean", lambda r: web.json_response())
    print("OK lean")
