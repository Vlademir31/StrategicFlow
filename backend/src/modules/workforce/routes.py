from aiohttp import web
def setup_workforce_routes(app):
    app.router.add_get("/api/v1/workforce", lambda r: web.json_response())
    print("OK workforce")
