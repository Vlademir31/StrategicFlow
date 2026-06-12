from aiohttp import web
from .service import get_companies, create_company, get_opportunities

def setup_crm_routes(app: web.Application):
    app.router.add_get("/crm/companies", list_companies)
    app.router.add_post("/crm/companies", add_company)
    app.router.add_get("/crm/opportunities", list_opportunities)

async def list_companies(request: web.Request) -> web.Response:
    tenant_id = request.get("tenant_id")
    if not tenant_id: return web.json_response({"error": "Não autorizado"}, status=401)
    return web.json_response({"companies": await get_companies(tenant_id)})

async def add_company(request: web.Request) -> web.Response:
    tenant_id = request.get("tenant_id")
    if not tenant_id: return web.json_response({"error": "Não autorizado"}, status=401)
    try:
        data = await request.json()
        new_comp = await create_company(data, tenant_id)
        return web.json_response(new_comp, status=201)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=400)

async def list_opportunities(request: web.Request) -> web.Response:
    tenant_id = request.get("tenant_id")
    if not tenant_id: return web.json_response({"error": "Não autorizado"}, status=401)
    return web.json_response({"opportunities": await get_opportunities(tenant_id)})
