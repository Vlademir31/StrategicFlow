import asyncpg
from datetime import datetime
from typing import List, Dict, Any, Optional

from .models import InventoryConsultiveView


class InventoryService:
    def __init__(self, request):
        self.request = request
        self.pool: asyncpg.pool.Pool = request.app["db"]

    # ============================================================
    #  LISTAGEM OPERACIONAL
    # ============================================================
    async def list_inventory(self) -> List[Dict[str, Any]]:
        tenant_id = self.request.headers.get("X-Tenant-ID", "default")

        query = """
            SELECT
                id,
                tenant_id,
                sku,
                sku_name,
                quantity_available,
                quantity_reserved,
                location,
                class_,
                unit_cost,
                avg_daily_consumption,
                safety_stock,
                max_stock,
                last_movement,
                last_updated
            FROM inventory
            WHERE tenant_id = $1
            ORDER BY sku
        """

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, tenant_id)

        return [dict(r) for r in rows]

    # ============================================================
    #  FUNÇÕES CONSULTIVAS
    # ============================================================
    def _calc_aging_days(self, last_movement: Optional[datetime]) -> Optional[int]:
        if not last_movement:
            return None
        return (datetime.utcnow() - last_movement).days

    def _calc_coverage_days(self, quantity_available: int, avg_daily_consumption: float) -> Optional[float]:
        if not avg_daily_consumption or avg_daily_consumption <= 0:
            return None
        return round(quantity_available / avg_daily_consumption, 2)

    def _calc_risk_of_stockout(self, coverage_days: Optional[float], safety_stock: int) -> Optional[bool]:
        if coverage_days is None:
            return None
        return coverage_days < safety_stock if safety_stock > 0 else None

    def _calc_has_excess(self, quantity_available: int, max_stock: int) -> Optional[bool]:
        if max_stock <= 0:
            return None
        return quantity_available > max_stock

    def _calc_stock_value(self, quantity_available: int, unit_cost: float) -> Optional[float]:
        if unit_cost is None:
            return None
        return round(quantity_available * unit_cost, 2)

    # ============================================================
    #  DASHBOARD CONSULTIVO
    # ============================================================
    async def inventory_dashboard(self) -> List[Dict[str, Any]]:
        tenant_id = self.request.headers.get("X-Tenant-ID", "default")

        query = """
            SELECT
                sku,
                sku_name,
                quantity_available,
                quantity_reserved,
                location,
                class_,
                unit_cost,
                avg_daily_consumption,
                safety_stock,
                max_stock,
                last_movement
            FROM inventory
            WHERE tenant_id = $1
            ORDER BY sku
        """

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, tenant_id)

        resultado: List[Dict[str, Any]] = []

        for r in rows:
            aging = self._calc_aging_days(r["last_movement"])
            coverage = self._calc_coverage_days(
                r["quantity_available"],
                float(r["avg_daily_consumption"] or 0)
            )
            risk = self._calc_risk_of_stockout(
                coverage,
                int(r["safety_stock"] or 0)
            )
            excess = self._calc_has_excess(
                r["quantity_available"],
                int(r["max_stock"] or 0)
            )
            stock_value = self._calc_stock_value(
                r["quantity_available"],
                float(r["unit_cost"] or 0)
            )

            view = InventoryConsultiveView(
                sku=r["sku"],
                sku_name=r["sku_name"],
                quantity_available=r["quantity_available"],
                quantity_reserved=r["quantity_reserved"],
                location=r["location"],
                class_=r["class_"],
                aging_days=aging,
                coverage_days=coverage,
                risk_of_stockout=risk,
                has_excess=excess,
                stock_value=stock_value,
            )

            resultado.append(view.__dict__)

        return resultado
