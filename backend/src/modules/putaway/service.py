# putaway_service.py
import asyncpg
from typing import List, Dict, Any

class PutawayService:
    def __init__(self, request):
        self.request = request
        self.pool: asyncpg.pool.Pool = request.app["db"]

    async def list_raw(self) -> List[Dict[str, Any]]:
        tenant_id = self.request.headers.get("X-Tenant-ID", "default")
        query = """
            SELECT *
            FROM putaway
            WHERE tenant_id = $1
            ORDER BY created_at DESC
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, tenant_id)
        return [dict(r) for r in rows]

    async def dashboard(self) -> Dict[str, Any]:
        data = await self.list_raw()
        total_tasks = len(data) or 1

        avg_total_time = sum((r.get("total_time_minutes") or 0) for r in data) / total_tasks
        avg_travel_time = sum((r.get("travel_time_minutes") or 0) for r in data) / total_tasks
        optimal_slots = sum(1 for r in data if r.get("is_optimal_slot"))
        non_optimal_slots = total_tasks - optimal_slots

        kpis = {
            "avg_total_time": avg_total_time,
            "avg_travel_time": avg_travel_time,
            "optimal_slot_rate": (optimal_slots / total_tasks) * 100,
            "non_optimal_slots": non_optimal_slots,
        }

        insights = []
        if avg_travel_time > 10:
            insights.append({"text": "Tempo médio de deslocamento alto — revisar layout e endereçamento."})
        if non_optimal_slots > 0:
            insights.append({"text": f"{non_optimal_slots} tarefas de putaway em slots não ideais."})

        alerts = []
        if kpis["optimal_slot_rate"] < 80:
            alerts.append({
                "level": "warning",
                "title": "Baixa taxa de slotting ideal",
                "message": f"Somente {kpis['optimal_slot_rate']:.1f}% dos putaways estão em slots ideais."
            })

        charts = {
            "tempo_por_tarefa": [
                {
                    "sku": r["sku"],
                    "total_time": r.get("total_time_minutes") or 0
                } for r in data
            ],
            "slotting_ideal": [
                {"label": "Ideal", "value": optimal_slots},
                {"label": "Não ideal", "value": non_optimal_slots},
            ],
            "produtividade_operador": self._produtividade_por_operador(data),
        }

        return {
            "kpis": kpis,
            "insights": insights,
            "alerts": alerts,
            "charts": charts,
            "raw": data,
        }

    def _produtividade_por_operador(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        ops: Dict[str, Dict[str, Any]] = {}
        for r in data:
            op = r.get("operator_name") or "N/A"
            if op not in ops:
                ops[op] = {"operator_name": op, "tasks": 0, "avg_time": 0}
            ops[op]["tasks"] += 1
            ops[op]["avg_time"] += (r.get("total_time_minutes") or 0)
        for v in ops.values():
            v["avg_time"] = v["avg_time"] / v["tasks"]
        return list(ops.values())
