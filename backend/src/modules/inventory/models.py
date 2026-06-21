from pydantic import BaseModel
from typing import Optional


# ============================================================
#  MODELO PARA CRIAÇÃO DE SKU (POST /inventory)
# ============================================================
class InventoryCreate(BaseModel):
    sku: str
    sku_name: Optional[str]
    quantity_available: int
    quantity_reserved: Optional[int] = 0
    location: Optional[str]
    class_: Optional[str] = "B"

    unit_cost: Optional[float] = 0
    avg_daily_consumption: Optional[float] = 0
    safety_stock: Optional[int] = 0
    max_stock: Optional[int] = 0


# ============================================================
#  MODELO PARA ATUALIZAÇÃO DE SKU (PUT /inventory/{sku})
# ============================================================
class InventoryUpdate(BaseModel):
    sku: Optional[str]
    sku_name: Optional[str]
    quantity_available: Optional[int]
    quantity_reserved: Optional[int]
    location: Optional[str]
    class_: Optional[str]

    unit_cost: Optional[float]
    avg_daily_consumption: Optional[float]
    safety_stock: Optional[int]
    max_stock: Optional[int]


# ============================================================
#  MODELO PARA RESPOSTA CONSULTIVA (DASHBOARD)
# ============================================================
class InventoryConsultiveResponse(BaseModel):
    sku: str
    sku_name: Optional[str]
    quantity_available: int
    quantity_reserved: int
    location: Optional[str]
    class_: str

    aging_days: Optional[int]
    coverage_days: Optional[float]
    risk_of_stockout: Optional[bool]
    has_excess: Optional[bool]
    stock_value: Optional[float]
