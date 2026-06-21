from aiohttp import web
def setup_integration_routes(app):
    app.router.add_get("/api/v1/integration", lambda r: web.json_response())
    print("OK integration")
