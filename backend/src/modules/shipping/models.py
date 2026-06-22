from dataclasses import dataclass
from datetime import datetime


@dataclass
class ShippingRecord:
    id: int
    tenant_id: str

    order_id: str
    sku: str
    sku_name: str | None
    quantity: int

    carrier: str | None
    tracking_code: str | None
    vehicle_type: str | None
    driver_name: str | None

    expedition_time_minutes: int
    loading_time_minutes: int
    waiting_time_minutes: int

    error_rate: float
    damage_rate: float
    rework: bool
    sla_compliance: bool

    shipped_at: datetime
    created_at: datetime
