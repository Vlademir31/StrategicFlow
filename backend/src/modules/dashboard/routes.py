from aiohttp import web

def setup_dashboard_routes(app):
    app.router.add_get("/api/v1/dashboard", lambda r: web.json_response())
    print("OK dashboard")
