from aiohttp import web
def setup_5s_routes(app):
    app.router.add_get("/api/v1/5s", lambda r: web.json_response())
    print("OK 5s")
