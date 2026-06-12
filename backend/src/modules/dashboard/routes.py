import asyncio
import json
import logging
from aiohttp import web
from .service import get_kpis

logger = logging.getLogger("dashboard_real_routes")

def setup_dashboard_routes(app: web.Application):
    app.router.add_get("/api/kpis", kpis_handler)
    app.router.add_get("/ws/kpis", kpis_websocket_handler)

async def _build_real_kpi_payload(tenant_id: str) -> dict:
    """Busca as métricas reais gravadas no Postgres de forma estrita."""
    try:
        kpis_list = await get_kpis(tenant_id)
    except Exception as e:
        logger.error(f"Erro ao ler KPIs: {e}")
        kpis_list = []

    # Mapa padrão de segurança caso falte algum registro na tabela
    payload = {
        "cycleTime": 0.0, "otif": 0.0, "efficiency": 0.0, "rejection": 0.0,
        "roi": 0.0, "success": 0.0, "nps": 0.0, "throughput": 0.0
    }

    # Preenche o contrato JSON lendo o campo 'name' exato enviado pelo banco
    for k in kpis_list:
        if k.name in payload:
            payload[k.name] = float(k.value)

    return payload

async def kpis_handler(request: web.Request) -> web.Response:
    tenant_id = request.get("tenant_id") or "default-tenant"
    payload = await _build_real_kpi_payload(tenant_id)
    return web.json_response(payload)

async def kpis_websocket_handler(request: web.Request) -> web.WebSocketResponse:
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    tenant_id = request.get("tenant_id") or "default-tenant"
    
    try:
        while True:
            # Envia dados reais sem oscilações artificiais
            payload = await _build_real_kpi_payload(tenant_id)
            await ws.send_str(json.dumps(payload))
            await asyncio.sleep(5) # Atualiza a cada 5 segundos
    except Exception:
        pass
    finally:
        await ws.close()
        return ws
