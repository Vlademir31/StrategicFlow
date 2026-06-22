from pydantic import BaseModel
from typing import Optional


class PackingCreate(BaseModel):
    order_id: str
    sku: str
    sku_name: Optional[str] = None
    quantity: int

    packing_type: Optional[str] = None      # caixa, envelope, pallet...
    operator_name: Optional[str] = None
    station: Optional[str] = None

    packing_time_minutes: Optional[int] = 0
    error_rate: Optional[float] = 0.0
    damage_rate: Optional[float] = 0.0
    rework: Optional[bool] = False
    sla_compliance: Optional[bool] = True


class PackingUpdate(BaseModel):
    quantity: Optional[int] = None
    packing_type: Optional[str] = None
    operator_name: Optional[str] = None
    station: Optional[str] = None

    packing_time_minutes: Optional[int] = None
    error_rate: Optional[float] = None
    damage_rate: Optional[float] = None
    rework: Optional[bool] = None
    sla_compliance: Optional[bool] = None
