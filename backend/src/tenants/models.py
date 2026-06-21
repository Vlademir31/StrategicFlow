from dataclasses import dataclass
from datetime import datetime

@dataclass
class Template:
    id: int
    tenant_id: str
    name: str
    category: str        # email, relatório, contrato, notificação
    description: str
    content: str         # corpo do template (texto/HTML)
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
@dataclass
class AuditLog:
    id: int
    tenant_id: str
    user_id: str
    action: str          # CREATE, UPDATE, DELETE, LOGIN, etc.
    module: str          # crm, financeiro, workforce, etc.
    entity_id: str       # ID do registro afetado
    description: str     # Detalhes da ação
    created_at: datetime = datetime.now()
