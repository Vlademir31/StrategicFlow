from aiohttp import web
def setup_vsm_routes(app):
    app.router.add_get("/api/v1/vsm", lambda r: web.json_response())
    print("OK vsm")
