from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TemplateCreate(BaseModel):
    name: str
    category: str
    description: Optional[str]
    content: str

class TemplateResponse(TemplateCreate):
    id: int
    tenant_id: str
    created_at: datetime
    updated_at: datetime
