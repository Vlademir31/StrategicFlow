import asyncpg
from typing import Dict, Any, List

class ShippingService:
    def __init__(self, request):
        self.request = request
        self.pool: asyncpg.pool.Pool = request.app["db"]

    async def list_raw(self):
        tenant = self.request.headers.get("X-Tenant-ID", "default")
        query = """
            SELECT *
            FROM shipping
            WHERE tenant_id = $1
            ORDER BY shipped_at DESC
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, tenant)
        return [dict(r) for r in rows]

    async def dashboard(self):
        data = await self.list_raw()
        total = len(data) or 1

        avg_expedition = sum((r.get("expedition_time_minutes") or 0) for r in data) / total
        avg_waiting = sum((r.get("waiting_time_minutes") or 0) for r in data) / total
        avg_damage = sum((r.get("damage_rate") or 0) for r in data) / total
        reworks = sum(1 for r in data if r.get("rework"))
        sla_ok = sum(1 for r in data if r.get("sla_compliance"))

        kpis = {
            "avg_expedition": avg_expedition,
            "avg_waiting": avg_waiting,
            "avg_damage": avg_damage,
            "reworks": reworks,
            "sla_rate": (sla_ok / total) * 100,
        }

        insights = []
        if avg_waiting > 15:
            insights.append({"text": "Tempo de espera elevado — gargalo na doca ou transportadora atrasada."})
        if avg_damage > 1:
            insights.append({"text": "Taxa de danos acima do ideal — revisar carregamento e amarração."})
        if reworks > 0:
            insights.append({"text": f"{reworks} pedidos tiveram retrabalho na expedição."})

        alerts = []
        if kpis["sla_rate"] < 95:
            alerts.append({
                "level": "warning",
                "title": "SLA de expedição abaixo do esperado",
                "message": f"SLA atual: {kpis['sla_rate']:.1f}%"
            })
        if avg_expedition > 20:
            alerts.append({
                "level": "danger",
                "title": "Tempo médio de expedição elevado",
                "message": f"Tempo médio: {avg_expedition:.1f} min"
            })

        charts = {
            "tempo_por_transportadora": self._tempo_por_carrier(data),
            "danos_por_sku": self._danos_por_sku(data),
            "espera_por_dia": self._espera_por_dia(data),
        }

        return {
            "kpis": kpis,
            "insights": insights,
            "alerts": alerts,
            "charts": charts,
            "raw": data,
        }

    def _tempo_por_carrier(self, data):
        c = {}
        for r in data:
            carrier = r.get("carrier") or "N/A"
            c.setdefault(carrier, []).append(r.get("expedition_time_minutes") or 0)
        return [{"carrier": k, "avg_time": sum(v)/len(v)} for k, v in c.items()]

    def _danos_por_sku(self, data):
        skus = {}
        for r in data:
            sku = r["sku"]
            skus.setdefault(sku, []).append(r.get("damage_rate") or 0)
        return [{"sku": k, "avg_damage": sum(v)/len(v)} for k, v in skus.items()]

    def _espera_por_dia(self, data):
        dias = {}
        for r in data:
            dia = r["shipped_at"].date().isoformat()
            dias.setdefault(dia, []).append(r.get("waiting_time_minutes") or 0)
        return [{"date": k, "avg_wait": sum(v)/len(v)} for k, v in dias.items()]
