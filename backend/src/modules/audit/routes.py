from aiohttp import web
def setup_audit_routes(app):
    app.router.add_get("/api/v1/audit", lambda r: web.json_response())
    print("OK audit")
