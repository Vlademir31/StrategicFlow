from dataclasses import dataclass
from datetime import datetime


@dataclass
class ReceivingRecord:
    id: int
    tenant_id: str
    nf_number: str
    sku: str
    quantity_expected: int
    quantity_received: int
    status: str
    cycle_time_hours: float
    operator_name: str
    created_at: datetime
