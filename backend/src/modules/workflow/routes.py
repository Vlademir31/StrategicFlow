from aiohttp import web
def setup_workflow_routes(app):
    app.router.add_get("/api/v1/workflow", lambda r: web.json_response())
    print("OK workflow")
