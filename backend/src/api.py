import logging
import asyncio
import os
from aiohttp import web
from typing import Callable, cast

from core.config import settings
from core.database import init_db
from core.middleware import setup_middlewares

# ✅ ROTAS ORIGINAIS (EXISTENTES)
from auth.routes import setup_auth_routes
from modules.dashboard.routes import setup_dashboard_routes  # type: ignore
from modules.inventory.routes import setup_inventory_routes  # type: ignore
from modules.receiving.routes import setup_receiving_routes  # type: ignore
from modules.picking.routes import setup_picking_routes  # type: ignore
from modules.crm.routes import setup_crm_routes  # type: ignore
from modules.projects.routes import setup_projects_routes  # type: ignore
from modules.lean.routes import setup_lean_routes  # type: ignore
from modules.realtime.routes import setup_realtime_routes  # type: ignore
from modules.financeiro.routes import setup_financeiro_routes  # type: ignore

# ✅ ROTAS DOS 8 MÓDULOS LEAN (ADICIONAR)
from modules.five_s.routes import setup_5s_routes as setup_5s_routes_raw  # type: ignore
from modules.kaizen.routes import setup_kaizen_routes  # type: ignore
from modules.pdca.routes import setup_pdca_routes as setup_pdca_routes_raw  # type: ignore
from modules.six_sigma.routes import setup_six_sigma_routes  # type: ignore
from modules.vsm.routes import setup_vsm_routes as setup_vsm_routes_raw  # type: ignore
from modules.workflow.routes import setup_workflow_routes as setup_workflow_routes_raw  # type: ignore
from modules.bpmn.routes import setup_bpmn_routes  # type: ignore
from modules.audit.routes import setup_audit_routes  # type: ignore

# Typing: ensure route setup callables are properly typed for static analysis
_RouteSetup = Callable[[web.Application], None]
setup_dashboard_routes = cast(_RouteSetup, setup_dashboard_routes)
setup_inventory_routes = cast(_RouteSetup, setup_inventory_routes)
setup_receiving_routes = cast(_RouteSetup, setup_receiving_routes)
setup_picking_routes = cast(_RouteSetup, setup_picking_routes)
setup_crm_routes = cast(_RouteSetup, setup_crm_routes)
setup_projects_routes = cast(_RouteSetup, setup_projects_routes)
setup_lean_routes = cast(_RouteSetup, setup_lean_routes)
setup_realtime_routes = cast(_RouteSetup, setup_realtime_routes)
setup_financeiro_routes = cast(_RouteSetup, setup_financeiro_routes)
setup_5s_routes = cast(_RouteSetup, setup_5s_routes_raw)
setup_kaizen_routes = cast(_RouteSetup, setup_kaizen_routes)
setup_pdca_routes = cast(_RouteSetup, setup_pdca_routes_raw)
setup_six_sigma_routes = cast(_RouteSetup, setup_six_sigma_routes)
setup_vsm_routes = cast(_RouteSetup, setup_vsm_routes_raw)
setup_workflow_routes = cast(_RouteSetup, setup_workflow_routes_raw)
setup_bpmn_routes = cast(_RouteSetup, setup_bpmn_routes)
setup_audit_routes = cast(_RouteSetup, setup_audit_routes)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


async def create_app() -> web.Application:
    app = web.Application()

    await init_db()
    setup_middlewares(app)  # <-- setup_middlewares já inclui auth + CORS

    setup_auth_routes(app)
    setup_dashboard_routes(app)
    setup_inventory_routes(app)
    setup_receiving_routes(app)
    setup_picking_routes(app)
    setup_crm_routes(app)
    setup_projects_routes(app)
    setup_lean_routes(app)
    setup_realtime_routes(app)
    setup_financeiro_routes(app)

    setup_5s_routes(app)
    setup_kaizen_routes(app)
    setup_pdca_routes(app)
    setup_six_sigma_routes(app)
    setup_vsm_routes(app)
    setup_workflow_routes(app)
    setup_bpmn_routes(app)
    setup_audit_routes(app)

    # ✅ FIXO: os.path.join
    backend_src = os.path.dirname(__file__)
    backend_dir = os.path.dirname(backend_src)
    project_root = os.path.dirname(backend_dir)
    frontend_dir = os.path.join(project_root, "frontend")
    
    print(f"🔍 Frontend DIR: {frontend_dir}")
    print(f"🔍 index.html exists: {os.path.exists(os.path.join(frontend_dir, 'index.html'))}")

    async def serve_index(request: web.Request):
        index_file = os.path.join(frontend_dir, 'index.html')
        if not os.path.exists(index_file):
            return web.Response(text=f"❌ index.html not found: {index_file}", status=500)
        return web.FileResponse(index_file)

    app.router.add_get("/", serve_index)
    app.router.add_static("/css/", os.path.join(frontend_dir, "css"))
    app.router.add_static("/js/", os.path.join(frontend_dir, "js"))

    print("🚀 Strategic Flow API iniciada!")
    print(f"🌐 Frontend: http://{settings.HOST}:{settings.PORT}/")
    print(f"🔌 API REST: http://{settings.HOST}:{settings.PORT}/api/")
    print("="*60)

    return app


def main():
    app = asyncio.run(create_app())
    web.run_app(app, host=settings.HOST, port=settings.PORT)


if __name__ == "__main__":
    main()