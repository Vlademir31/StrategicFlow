from aiohttp import web
def setup_bi_routes(app):
    app.router.add_get("/api/v1/bi", lambda r: web.json_response())
    print("OK bi")
