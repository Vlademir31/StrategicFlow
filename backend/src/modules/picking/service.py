import asyncpg
from typing import List, Dict, Any

class PickingService:
    def __init__(self, request):
        self.request = request
        self.pool: asyncpg.pool.Pool = request.app["db"]

    async def list_raw(self):
        tenant_id = self.request.headers.get("X-Tenant-ID", "default")
        query = """
            SELECT *
            FROM picking
            WHERE tenant_id = $1
            ORDER BY picked_at DESC
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, tenant_id)
        return [dict(r) for r in rows]

    async def dashboard(self):
        data = await self.list_raw()
        total = len(data) or 1

        # KPIs
        avg_time = sum((r.get("picking_time_minutes") or 0) for r in data) / total
        avg_error = sum((r.get("error_rate") or 0) for r in data) / total
        avg_prod = sum((r.get("productivity_units_per_hour") or 0) for r in data) / total
        divergences = sum(1 for r in data if r.get("divergence"))
        sla_ok = sum(1 for r in data if r.get("sla_compliance"))

        kpis = {
            "avg_time": avg_time,
            "avg_error": avg_error,
            "avg_productivity": avg_prod,
            "divergences": divergences,
            "sla_rate": (sla_ok / total) * 100,
        }

        # Insights
        insights = []
        if avg_error > 3:
            insights.append({"text": "Taxa de erro acima do normal — revisar processo de conferência."})
        if avg_prod < 40:
            insights.append({"text": "Produtividade baixa — operadores podem estar sobrecarregados."})
        if divergences > 0:
            insights.append({"text": f"{divergences} pedidos tiveram divergência no picking."})

        # Alertas
        alerts = []
        if kpis["sla_rate"] < 90:
            alerts.append({
                "level": "danger",
                "title": "SLA abaixo do esperado",
                "message": f"SLA atual: {kpis['sla_rate']:.1f}%"
            })
        if avg_error > 5:
            alerts.append({
                "level": "warning",
                "title": "Erro elevado",
                "message": f"Taxa de erro média: {avg_error:.1f}%"
            })

        # Gráficos
        charts = {
            "prod_por_operador": self._prod_por_operador(data),
            "erros_por_sku": self._erros_por_sku(data),
            "tempo_por_dia": self._tempo_por_dia(data),
        }

        return {
            "kpis": kpis,
            "insights": insights,
            "alerts": alerts,
            "charts": charts,
            "raw": data,
        }

    def _prod_por_operador(self, data):
        ops = {}
        for r in data:
            op = r.get("operator_name") or "N/A"
            ops.setdefault(op, []).append(r.get("productivity_units_per_hour") or 0)
        return [{"operator": k, "avg_prod": sum(v)/len(v)} for k, v in ops.items()]

    def _erros_por_sku(self, data):
        skus = {}
        for r in data:
            sku = r["sku"]
            skus.setdefault(sku, []).append(r.get("error_rate") or 0)
        return [{"sku": k, "avg_error": sum(v)/len(v)} for k, v in skus.items()]

    def _tempo_por_dia(self, data):
        dias = {}
        for r in data:
            dia = r["picked_at"].date().isoformat()
            dias.setdefault(dia, []).append(r.get("picking_time_minutes") or 0)
        return [{"date": k, "avg_time": sum(v)/len(v)} for k, v in dias.items()]
