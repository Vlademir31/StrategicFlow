from aiohttp import web
def setup_kpis_routes(app):
    app.router.add_get("/api/v1/kpis", lambda r: web.json_response())
    print("OK kpis")
