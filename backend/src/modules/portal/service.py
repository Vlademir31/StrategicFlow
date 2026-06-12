from core.database import get_db
from .schemas import CommentSchema

async def get_client_project_status(tenant_id: str, client_email: str) -> dict | None:
    """Busca os dados gerais do projeto contratado pelo cliente logado."""
    db = await get_db()
    query = """
        SELECT 
            p.id_projeto,
            c.razao_social as empresa,
            p.escopo_servico,
            p.status_projeto,
            p.data_inicio,
            p.data_fim,
            p.valor_contratado::float
        FROM users u
        JOIN crm_companies c ON u.id_empresa = c.id_empresa
        JOIN crm_projects p ON c.id_empresa = p.id_empresa
        WHERE u.tenant_id = $1 AND u.email = $2;
    """
    row = await db.fetchrow(query, tenant_id, client_email)
    return dict(row) if row else None

async def get_client_processes(tenant_id: str, client_email: str) -> list[dict]:
    """Lista apenas os processos do projeto do cliente liberados pela consultoria."""
    db = await get_db()
    query = """
        SELECT 
            p.id_processo,
            p.nome_processo,
            p.xml_bpmn,
            p.created_at
        FROM portal_mapped_processes p
        JOIN users u ON u.id_empresa = p.id_empresa AND u.id_projeto = p.id_projeto
        WHERE u.tenant_id = $1 
          AND u.email = $2 
          AND p.visivel_portal = TRUE
        ORDER BY p.nome_processo;
    """
    rows = await db.fetch(query, tenant_id, client_email)
    return [dict(row) for row in rows]

async def get_process_comments(tenant_id: str, id_processo: int) -> list[dict]:
    """Recupera a linha do tempo de comentários de um processo específico."""
    db = await get_db()
    query = """
        SELECT id_comentario, usuario_nome, usuario_email, messaging_text as mensagem, created_at
        FROM portal_comments
        WHERE tenant_id = $1 AND id_processo = $2
        ORDER BY created_at ASC;
    """
    # Nota técnica: Alterado 'mensagem' para 'messaging_text' se necessário, 
    # mas mantido o apelido/alias para bater com seu banco e contrato JSON.
    query_corrected = """
        SELECT id_comentario, usuario_nome, usuario_email, mensagem, created_at
        FROM portal_comments
        WHERE tenant_id = $1 AND id_processo = $2
        ORDER BY created_at ASC;
    """
    rows = await db.fetch(query_corrected, tenant_id, id_processo)
    return [dict(row) for row in rows]

async def create_process_comment(tenant_id: str, data: dict, user_email: str, user_name: str) -> dict:
    """Salva o comentário enviado pelo usuário (cliente ou consultor)."""
    schema = CommentSchema(**data)
    db = await get_db()
    query = """
        INSERT INTO portal_comments (tenant_id, id_processo, usuario_email, usuario_nome, mensagem)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id_comentario, usuario_nome, usuario_email, mensagem, created_at;
    """
    row = await db.fetchrow(query, tenant_id, schema.id_processo, user_email, user_name, schema.mensagem)
    return dict(row)
