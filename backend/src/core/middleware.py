from aiohttp import web
from typing import Any, Awaitable, Callable, cast
from core.security import decode_token  # type: ignore[reportUnknownVariableType]


def setup_middlewares(app: web.Application):

        @web.middleware
    async def auth_tenant_middleware(
        request: web.Request,
        handler: cast(Any, None),
    ) -> web.StreamResponse:
        
        # ---> ADICIONADO: Se for a rota do WebSocket, ignora validação estrita de header
        if request.path == "/ws/kpis":
            request["tenant_id"] = "default-tenant"
            request["user"] = "consultor-live"
            return await handler(request)

        auth_header = request.headers.get("Authorization")
        request["tenant_id"] = None
        request["user"] = None
        
    @web.middleware
    async def auth_tenant_middleware(
        request: web.Request,
        handler: Callable[[web.Request], Awaitable[web.StreamResponse]],
    ) -> web.StreamResponse:
        auth_header = request.headers.get("Authorization")
        request["tenant_id"] = None
        request["user"] = None

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
            try:
                payload = cast(dict[str, Any], decode_token(token))
                request["tenant_id"] = payload.get("tenant_id")
                request["user"] = payload.get("sub")
            except Exception:
                pass

        return await handler(request)

    @web.middleware
    async def cors_middleware(
        request: web.Request,
        handler: Callable[[web.Request], Awaitable[web.StreamResponse]],
    ) -> web.StreamResponse:
        if request.method == "OPTIONS":
            resp: web.StreamResponse = web.Response(status=200)
        else:
            resp = await handler(request)

        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Headers"] = "*"
        resp.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
        return resp

    app.middlewares.append(auth_tenant_middleware)
    app.middlewares.append(cors_middleware)
