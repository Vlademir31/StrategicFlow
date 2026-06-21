from aiohttp import web
def setup_notifications_routes(app):
    app.router.add_get("/api/v1/notifications", lambda r: web.json_response())
    print("OK notifications")
