import asyncpg
from typing import Dict, Any, List

class PackingService:
    def __init__(self, request):
        self.request = request
        self.pool: asyncpg.pool.Pool = request.app["db"]

    async def list_raw(self) -> List[Dict[str, Any]]:
        tenant_id = self.request.headers.get("X-Tenant-ID", "default")
        query = """
            SELECT *
            FROM packing
            WHERE tenant_id = $1
            ORDER BY packed_at DESC
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, tenant_id)
        return [dict(r) for r in rows]

    async def dashboard(self) -> Dict[str, Any]:
        data = await self.list_raw()
        total = len(data) or 1

        avg_time = sum((r.get("packing_time_minutes") or 0) for r in data) / total
        avg_error = sum((r.get("error_rate") or 0) for r in data) / total
        avg_damage = sum((r.get("damage_rate") or 0) for r in data) / total
        reworks = sum(1 for r in data if r.get("rework"))
        sla_ok = sum(1 for r in data if r.get("sla_compliance"))

        kpis = {
            "avg_time": avg_time,
            "avg_error": avg_error,
            "avg_damage": avg_damage,
            "reworks": reworks,
            "sla_rate": (sla_ok / total) * 100,
        }

        insights = []
        if avg_error > 2:
            insights.append({"text": "Taxa de erro de packing acima do ideal — revisar conferência final."})
        if avg_damage > 1:
            insights.append({"text": "Há danos recorrentes — revisar materiais e padrão de embalagem."})
        if reworks > 0:
            insights.append({"text": f"{reworks} pedidos tiveram retrabalho no packing."})

        alerts = []
        if kpis["sla_rate"] < 95:
            alerts.append({
                "level": "warning",
                "title": "SLA de packing abaixo do alvo",
                "message": f"SLA atual: {kpis['sla_rate']:.1f}%"
            })
        if avg_time > 10:
            alerts.append({
                "level": "danger",
                "title": "Tempo médio de packing elevado",
                "message": f"Tempo médio: {avg_time:.1f} min"
            })

        charts = {
            "tempo_por_station": self._tempo_por_station(data),
            "erros_por_sku": self._erros_por_sku(data),
            "damage_por_tipo": self._damage_por_tipo(data),
        }

        return {
            "kpis": kpis,
            "insights": insights,
            "alerts": alerts,
            "charts": charts,
            "raw": data,
        }

    def _tempo_por_station(self, data):
        st = {}
        for r in data:
            s = r.get("station") or "N/A"
            st.setdefault(s, []).append(r.get("packing_time_minutes") or 0)
        return [{"station": k, "avg_time": sum(v)/len(v)} for k, v in st.items()]

    def _erros_por_sku(self, data):
        skus = {}
        for r in data:
            sku = r["sku"]
            skus.setdefault(sku, []).append(r.get("error_rate") or 0)
        return [{"sku": k, "avg_error": sum(v)/len(v)} for k, v in skus.items()]

    def _damage_por_tipo(self, data):
        tipos = {}
        for r in data:
            t = r.get("packing_type") or "N/A"
            tipos.setdefault(t, []).append(r.get("damage_rate") or 0)
        return [{"type": k, "avg_damage": sum(v)/len(v)} for k, v in tipos.items()]
