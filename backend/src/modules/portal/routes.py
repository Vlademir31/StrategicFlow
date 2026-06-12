from aiohttp import web
from .service import (
    get_client_project_status,
    get_client_processes,
    get_process_comments,
    create_process_comment,
)


def setup_portal_routes(app: web.Application):
    app.router.add_get("/api/portal/my-project", client_project_handler)
    app.router.add_get("/api/portal/my-processes", client_processes_handler)
    app.router.add_get("/api/portal/comments/{id_processo}", list_comments_handler)
    app.router.add_post("/api/portal/comments", add_comment_handler)


async def client_project_handler(request: web.Request) -> web.Response:
    tenant_id = request.get("tenant_id")
    client_email = request.get("user")

    if not tenant_id or not client_email:
        return web.json_response(
            {"error": "Sessão inválida ou não autenticada."}, status=401
        )

    project_data = await get_client_project_status(tenant_id, client_email)
    if not project_data:
        return web.json_response(
            {"error": "Nenhum projeto ativo encontrado para este usuário."}, status=404
        )

    return web.json_response(project_data)


async def client_processes_handler(request: web.Request) -> web.Response:
    tenant_id = request.get("tenant_id")
    client_email = request.get("user")

    if not tenant_id or not client_email:
        return web.json_response(
            {"error": "Sessão inválida ou não autenticada."}, status=401
        )

    processes = await get_client_processes(tenant_id, client_email)
    return web.json_response({"processes": processes})


async def list_comments_handler(request: web.Request) -> web.Response:
    tenant_id = request.get("tenant_id")
    if not tenant_id:
        return web.json_response({"error": "Não autorizado"}, status=401)

    try:
        id_processo = int(request.match_info["id_processo"])
        comments = await get_process_comments(tenant_id, id_processo)
        return web.json_response({"comments": comments})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=400)


async def add_comment_handler(request: web.Request) -> web.Response:
    tenant_id = request.get("tenant_id")
    user_email = request.get("user")

    # Busca dinamicamente o nome do usuário injetado, ou define um fallback seguro
    user_name = request.get("user_name", "Usuário do Portal")

    if not tenant_id or not user_email:
        return web.json_response({"error": "Sessão inválida ou expirada."}, status=401)

    try:
        data = await request.json()
        new_comment = await create_process_comment(
            tenant_id, data, user_email, user_name
        )
        return web.json_response(new_comment, status=201)
    except Exception as e:
        return web.json_response(
            {"error": f"Erro ao enviar comentário: {str(e)}"}, status=400
        )
