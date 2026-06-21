from aiohttp import web
def setup_pdca_routes(app):
    app.router.add_get("/api/v1/pdca", lambda r: web.json_response())
    print("OK pdca")
