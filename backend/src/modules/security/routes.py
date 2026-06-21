from aiohttp import web
def setup_security_routes(app):
    app.router.add_get("/api/v1/security", lambda r: web.json_response())
    print("OK security")
