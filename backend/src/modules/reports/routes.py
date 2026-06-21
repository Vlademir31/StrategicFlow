from aiohttp import web
def setup_reports_routes(app):
    app.router.add_get("/api/v1/reports", lambda r: web.json_response())
    print("OK reports")
