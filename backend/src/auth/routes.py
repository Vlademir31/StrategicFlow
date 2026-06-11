from aiohttp import web
from .service import register_user, login_user


def setup_auth_routes(app: web.Application):
    app.router.add_post("/auth/register", register_handler)
    app.router.add_post("/auth/login", login_handler)


async def register_handler(request: web.Request):
    data = await request.json()
    user = await register_user(data)
    return web.json_response({"user": user})


async def login_handler(request: web.Request):
    data = await request.json()
    try:
        token = await login_user(data)
        return web.json_response({"access_token": token})
    except ValueError:
        raise web.HTTPUnauthorized(text="Credenciais inválidas")
