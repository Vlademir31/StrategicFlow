from aiohttp import web

@web.middleware
async def tenant_middleware(request: web.Request, handler):
    """
    Middleware para identificar o tenant da requisição.
    Pode usar cabeçalho, subdomínio ou token JWT.
    """
    tenant_id = request.headers.get("X-Tenant-ID")
    user_email = request.headers.get("X-User-Email")
    user_name = request.headers.get("X-User-Name")

    # Injeta no request para uso nos handlers
    if tenant_id:
        request["tenant_id"] = tenant_id
    if user_email:
        request["user"] = user_email
    if user_name:
        request["user_name"] = user_name

    response = await handler(request)
    return response
