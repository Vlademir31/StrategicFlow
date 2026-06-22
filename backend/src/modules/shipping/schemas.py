from pydantic import BaseModel
from typing import Optional

class ShippingCreate(BaseModel):
    order_id: str
    sku: str
    sku_name: Optional[str] = None
    quantity: int

    carrier: Optional[str] = None
    tracking_code: Optional[str] = None
    vehicle_type: Optional[str] = None
    driver_name: Optional[str] = None

class ShippingUpdate(BaseModel):
    expedition_time_minutes: Optional[int]
    loading_time_minutes: Optional[int]
    waiting_time_minutes: Optional[int]

    error_rate: Optional[float]
    damage_rate: Optional[float]
    rework: Optional[bool]
    sla_compliance: Optional[bool]
