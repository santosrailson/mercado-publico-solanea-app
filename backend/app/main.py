from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.db.database import engine, Base
from app.api import auth, cessionarios, pagamentos, dashboard, relatorios, users, fiscais
from app.db.seed import seed_data

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    seed_data()
    yield
    # Shutdown


from slowapi import _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from app.core.rate_limit import limiter

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan
)

# Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(cessionarios.router, prefix="/api/v1")
app.include_router(pagamentos.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(relatorios.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(fiscais.router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "message": "Mercado Público API",
        "version": settings.VERSION,
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
