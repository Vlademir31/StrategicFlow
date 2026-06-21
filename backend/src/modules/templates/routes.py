from aiohttp import web
def setup_templates_routes(app):
    app.router.add_get("/api/v1/templates", lambda r: web.json_response())
    print("OK templates")
