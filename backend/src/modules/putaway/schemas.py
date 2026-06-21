from pydantic import BaseModel
from typing import Optional

class PutawayCreate(BaseModel):
    sku: str
    sku_name: Optional[str] = None
    quantity: int
    source_location: Optional[str] = None
    target_location: Optional[str] = None
    class_: Optional[str] = "B"
    operator_name: Optional[str] = None

class PutawayUpdate(BaseModel):
    quantity: Optional[int]
    source_location: Optional[str]
    target_location: Optional[str]
    class_: Optional[str]
    operator_name: Optional[str]
    task_status: Optional[str]
    travel_time_minutes: Optional[int]
    handling_time_minutes: Optional[int]
    total_time_minutes: Optional[int]
    is_optimal_slot: Optional[bool]
