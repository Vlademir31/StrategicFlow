from aiohttp import web
from core.security import decode_token


def setup_middlewares(app: web.Application):
    @web.middleware
    async def auth_tenant_middleware(request, handler):
        auth_header = request.headers.get("Authorization")
        request["tenant_id"] = None
        request["user"] = None

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
            try:
                payload = decode_token(token)
                request["tenant_id"] = payload.get("tenant_id")
                request["user"] = payload.get("sub")
            except Exception:
                pass

        return await handler(request)

    @web.middleware
    async def cors_middleware(request, handler):
        if request.method == "OPTIONS":
            resp = web.Response(status=200)
        else:
            resp = await handler(request)

        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Headers"] = "*"
        resp.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
        return resp

    app.middlewares.append(auth_tenant_middleware)
    app.middlewares.append(cors_middleware)
