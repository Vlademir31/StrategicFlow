from aiohttp import web
def setup_six_sigma_routes(app):
    app.router.add_get("/api/v1/six_sigma", lambda r: web.json_response())
    print("OK six_sigma")
