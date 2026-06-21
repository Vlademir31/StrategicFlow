from aiohttp import web
def setup_quality_routes(app):
    app.router.add_get("/api/v1/quality", lambda r: web.json_response())
    print("OK quality")
