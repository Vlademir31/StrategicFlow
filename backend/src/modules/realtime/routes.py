from aiohttp import web

def setup_realtime_routes(app):
    app.router.add_get("/api/v1/realtime", lambda r: web.json_response())
    print("OK realtime")
