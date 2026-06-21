from aiohttp import web
def setup_mobile_routes(app):
    app.router.add_get("/api/v1/mobile", lambda r: web.json_response())
    print("OK mobile")
