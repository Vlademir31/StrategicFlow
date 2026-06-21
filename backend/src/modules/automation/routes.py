from aiohttp import web

def setup_automation_routes(app):
    app.router.add_get("/api/v1/automation", lambda r: web.json_response())
    print("OK automation")
