from aiohttp import web
from core.security import create_access_token
ADMIN_USER = {"email": "admin@strategicflow.com", "password": "admin123"}
async def login(request: web.Request):
    data = await request.json()
    if data.get("email") == ADMIN_USER["email"] and data.get("password") == ADMIN_USER["password"]:
        token = create_access_token(sub=ADMIN_USER["email"], tenant_id="default", role="consultor")
        return web.json_response({"access_token": token})
    return web.json_response({"error": "Invalid"}, status=401)
def setup_auth_routes(app: web.Application):
    app.router.add_post("/api/v1/auth/login", login)
    print("✅ Auth")
