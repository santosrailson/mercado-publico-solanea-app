import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from database import init_db
from routers import auth, users, cessionarios, pagamentos, relatorios

limiter = Limiter(key_func=get_remote_address)

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Mercado Público de Solânea – Sistema de Gestão",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routers — all under /api prefix
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(cessionarios.router, prefix="/api")
app.include_router(pagamentos.router, prefix="/api")
app.include_router(relatorios.router, prefix="/api")

# Serve frontend static files
FRONTEND_DIR_ABS = os.path.abspath(FRONTEND_DIR)

if os.path.isdir(FRONTEND_DIR_ABS):
    @app.get("/", include_in_schema=False)
    async def root():
        return FileResponse(os.path.join(FRONTEND_DIR_ABS, "index.html"))

    @app.get("/styles.css", include_in_schema=False)
    async def serve_css():
        return FileResponse(os.path.join(FRONTEND_DIR_ABS, "styles.css"), media_type="text/css")

    @app.get("/app.js", include_in_schema=False)
    async def serve_js():
        return FileResponse(os.path.join(FRONTEND_DIR_ABS, "app.js"), media_type="application/javascript")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str, request: Request):
        # Try to serve as a static file, otherwise return index.html
        candidate = os.path.join(FRONTEND_DIR_ABS, full_path)
        if os.path.isfile(candidate):
            return FileResponse(candidate)
        return FileResponse(os.path.join(FRONTEND_DIR_ABS, "index.html"))
