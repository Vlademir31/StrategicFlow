from aiohttp import web
def setup_portal_routes(app):
    app.router.add_get("/api/v1/portal", lambda r: web.json_response())
    print("OK portal")
