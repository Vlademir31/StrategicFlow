from aiohttp import web
from .service import create_template, list_templates, get_template_by_id
from .schemas import TemplateCreate


def setup_templates_routes(app: web.Application):
    app.router.add_post("/api/templates", create_template_handler)
    app.router.add_get("/api/templates", list_templates_handler)
    app.router.add_get("/api/templates/{id}", get_template_handler)
    print("✅ Rotas Templates registradas: /api/templates, /api/templates/{id}")


async def create_template_handler(request: web.Request) -> web.Response:
    tenant_id = request.get("tenant_id") or "default-tenant"
    data = await request.json()
    payload = TemplateCreate(**data)
    result = await create_template(payload.dict(), tenant_id)
    return web.json_response(result, status=201)


async def list_templates_handler(request: web.Request) -> web.Response:
    tenant_id = request.get("tenant_id") or "default-tenant"
    templates = await list_templates(tenant_id)
    return web.json_response({"templates": templates})


async def get_template_handler(request: web.Request) -> web.Response:
    tenant_id = request.get("tenant_id") or "default-tenant"
    template_id = int(request.match_info["id"])
    template = await get_template_by_id(template_id, tenant_id)
    if not template:
        return web.json_response({"error": "Template não encontrado"}, status=404)
    return web.json_response(template)
