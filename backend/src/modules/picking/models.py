from dataclasses import dataclass
from datetime import datetime

@dataclass
class PickingRecord:
    id: int
    tenant_id: str
    order_id: str
    sku: str
    sku_name: str | None
    quantity: int
    zone: str | None
    operator_name: str | None
    picking_time_minutes: int
    travel_time_minutes: int
    handling_time_minutes: int
    productivity_units_per_hour: float
    error_rate: float
    divergence: bool
    sla_compliance: bool
    picked_at: datetime
    created_at: datetime
