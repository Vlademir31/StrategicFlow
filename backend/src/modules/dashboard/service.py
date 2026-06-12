from core.database import get_db

async def get_kpis_flat_object(tenant_id: str) -> dict:
    """Busca as 8 chaves reais diretamente do banco e mapeia em formato plano."""
    db = await get_db()
    
    # Dicionário com fallbacks seguros de desenvolvimento
    payload = {
        "cycleTime": 0.0, "otif": 0.0, "efficiency": 0.0, "rejection": 0.0,
        "roi": 0.0, "success": 0.0, "nps": 0.0, "throughput": 0.0
    }
    
    rows = await db.fetch(
        "SELECT name, value FROM kpis WHERE tenant_id = $1", 
        tenant_id
    )
    
    for r in rows:
        key_name = r["name"].strip()
        if key_name in payload:
            payload[key_name] = float(r["value"])
            
    return payload
