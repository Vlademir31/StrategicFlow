from aiohttp import web
from typing import Any, Awaitable, Callable
import logging
from core.security import decode_token

logger = logging.getLogger("middlewares")


def setup_middlewares(app: web.Application):
    """Configura middlewares: Auth Tenant + CORS"""

    @web.middleware
    async def auth_tenant_middleware(
        request: web.Request,
        handler: Callable[[web.Request], Awaitable[web.StreamResponse]],
    ) -> web.StreamResponse:
        """
        Middleware de autenticação e tenant identification.
        - Ignora validação para arquivos estáticos
        - Ignora validação para WebSocket
        - Ignora validação para rotas públicas
        """

        path = request.url.path

        # 🔓 Arquivos estáticos SEM autenticação
        if (
            path.startswith("/css/")
            or path.startswith("/js/")
            or path.startswith("/images/")
            or path.startswith("/static/")
            or path == "/favicon.ico"
        ):
            return await handler(request)

        # 🔓 Página inicial SEM autenticação
        if path == "/":
            return await handler(request)

        # 🔓 WebSocket SEM autenticação
        if path.startswith("/ws/"):
            request["tenant_id"] = "default-tenant"
            request["user"] = {"email": "ws-client", "tenant_id": "default-tenant"}
            return await handler(request)

        # 🔓 Rotas públicas
        if path in ["/swagger.json", "/health"]:
            return await handler(request)

        # 🔓 API pública (se você quiser proteger, remova este bloco)
        if path.startswith("/api/"):
            request["tenant_id"] = "default-tenant"
            request["user"] = {"email": "public-api", "tenant_id": "default-tenant"}
            return await handler(request)

        # 🔐 A partir daqui, exige token
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return web.json_response(
                {"error": "Authorization header required"},
                status=401,
            )

        try:
            token = auth_header.replace("Bearer ", "").strip()
            user_payload = decode_token(token)

            request["user"] = user_payload
            request["tenant_id"] = user_payload.get("tenant_id")

            if not request["tenant_id"]:
                return web.json_response(
                    {"error": "tenant_id required in token"},
                    status=401,
                )

            logger.info(
                f"[AUTH] User: {user_payload.get('email')} | Tenant: {request['tenant_id']}"
            )

        except Exception as e:
            logger.error(f"[AUTH] Token decoding failed: {e}")
            return web.json_response({"error": "Invalid token"}, status=401)

        return await handler(request)

    app.middlewares.append(auth_tenant_middleware)
    logger.info("[MIDDLEWARES] Auth tenant middleware registrado.")


@web.middleware
async def cors_middleware(
    request: web.Request,
    handler: Callable[[web.Request], Awaitable[web.StreamResponse]],
) -> web.StreamResponse:
    """CORS middleware simples"""
    response = await handler(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
    return response


def setup_cors(app: web.Application):
    """Registra CORS"""
    app.middlewares.append(cors_middleware)
    logger.info("[CORS] CORS middleware registrado.")
