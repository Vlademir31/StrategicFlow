from aiohttp import web

def setup_crm_routes(app):
    app.router.add_get("/api/v1/crm", lambda r: web.json_response())
    print("OK crm")
