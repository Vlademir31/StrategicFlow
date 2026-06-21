from aiohttp import web
def setup_diagnostics_routes(app):
    app.router.add_get("/api/v1/diagnostics", lambda r: web.json_response())
    print("OK diagnostics")
