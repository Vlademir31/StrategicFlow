# putaway_models.py
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PutawayRecord:
    id: int
    tenant_id: str
    sku: str
    sku_name: str | None
    quantity: int
    source_location: str | None
    target_location: str | None
    class_: str
    operator_name: str | None
    task_status: str
    travel_time_minutes: int | None
    handling_time_minutes: int | None
    total_time_minutes: int | None
    is_optimal_slot: bool
    created_at: datetime
