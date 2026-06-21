from aiohttp import web
def setup_bpmn_routes(app):
    app.router.add_get("/api/v1/bpmn", lambda r: web.json_response())
    print("OK bpmn")
