import logging 

logging.basicConfig(level=logging.INFO)

import asyncio
import os
from aiohttp import web

from core.config import settings
from core.database import init_db
from core.middleware import setup_middlewares

from auth.routes import setup_auth_routes
from modules.dashboard.routes import setup_dashboard_routes


async def create_app() -> web.Application:
    app = web.Application()

    await init_db()
    setup_middlewares(app)

    setup_auth_routes(app)
    setup_dashboard_routes(app)

    # servir frontend
    frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')

    async def serve_index(request: web.Request):
        return web.FileResponse(os.path.join(frontend_dir, 'index.html'))

    app.router.add_get("/", serve_index)
    app.router.add_static("/css/", os.path.join(frontend_dir, "css"))
    app.router.add_static("/js/", os.path.join(frontend_dir, "js"))

    print("🚀 Strategic Flow API iniciada!")
    print(f"🌐 Frontend: http://{settings.HOST}:{settings.PORT}/")

    return app


def main():
    app = asyncio.run(create_app())
    web.run_app(app, host=settings.HOST, port=settings.PORT)


if __name__ == "__main__":
    main()
