from pydantic import BaseModel
from typing import Optional


class ReceivingCreate(BaseModel):
    nf_number: str
    sku: str
    quantity_expected: int
    quantity_received: Optional[int] = 0
    status: Optional[str] = "em_processo"
    cycle_time_hours: Optional[float] = None
    operator_name: str


class ReceivingUpdate(BaseModel):
    nf_number: Optional[str]
    sku: Optional[str]
    quantity_expected: Optional[int]
    quantity_received: Optional[int]
    status: Optional[str]
    cycle_time_hours: Optional[float]
    operator_name: Optional[str]
