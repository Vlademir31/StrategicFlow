from aiohttp import web
from .service import get_consultants_dashboard, create_consultant

def setup_workforce_routes(app: web.Application):
    app.router.add_get("/api/workforce/dashboard", workforce_dashboard_handler)
    app.router.add_post("/api/workforce/consultants", add_consultant_handler)

async def workforce_dashboard_handler(request: web.Request) -> web.Response:
    tenant_id = request.get("tenant_id")
    if not tenant_id:
        return web.json_response({"error": "Não autorizado"}, status=401)
        
    data = await get_consultants_dashboard(tenant_id)
    return web.json_response({"consultants": data})

async def add_consultant_handler(request: web.Request) -> web.Response:
    tenant_id = request.get("tenant_id")
    if not tenant_id:
        return web.json_response({"error": "Não autorizado"}, status=401)
    try:
        data = await request.json()
        new_consultant = await create_consultant(data, tenant_id)
        return web.json_response(new_consultant, status=201)
    except Exception as e:
        return web.json_response({"error": f"Erro ao processar: {str(e)}"}, status=400)
