from pydantic import BaseModel
from typing import Optional

class PickingCreate(BaseModel):
    order_id: str
    sku: str
    sku_name: Optional[str] = None
    quantity: int
    zone: Optional[str] = None
    operator_name: Optional[str] = None

class PickingUpdate(BaseModel):
    quantity: Optional[int]
    zone: Optional[str]
    operator_name: Optional[str]
    picking_time_minutes: Optional[int]
    travel_time_minutes: Optional[int]
    handling_time_minutes: Optional[int]
    productivity_units_per_hour: Optional[float]
    error_rate: Optional[float]
    divergence: Optional[bool]
    sla_compliance: Optional[bool]
