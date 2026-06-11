from dataclasses import dataclass

@dataclass
class Kpi:
    name: str
    value: float
    unit: str
    tenant_id: str
