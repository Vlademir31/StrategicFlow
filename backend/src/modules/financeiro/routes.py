from aiohttp import web
def setup_financeiro_routes(app):
    app.router.add_get("/api/v1/financeiro", lambda r: web.json_response())
    print("OK financeiro")
