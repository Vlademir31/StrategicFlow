from aiohttp import web

def setup_projects_routes(app):
    app.router.add_get("/api/v1/projects", lambda r: web.json_response())
    print("OK projects")
