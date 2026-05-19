from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.common.rate_limit import limiter
from src.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    settings = get_settings()
    if not settings.is_production:
        print(f"Starting {settings.app_name} in {settings.app_env} mode")
    yield
    print("Shutting down")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        lifespan=lifespan,
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    if settings.is_production:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origin_list,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    else:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=False,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    from src.auth.router import router as auth_router
    from src.plans.router import router as plans_router
    from src.progress.router import router as progress_router
    from src.quiz.router import router as quiz_router
    from src.tasks.router import router as tasks_router

    app.include_router(auth_router)
    app.include_router(quiz_router)
    app.include_router(plans_router)
    app.include_router(tasks_router)
    app.include_router(progress_router)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()


"""
=== FILE FLOW DOCUMENTATION ===

Functionality: FastAPI application factory with CORS, rate limiting, and health check.

Flow:
1. create_app() builds the FastAPI instance with middleware
2. CORS configured from settings.cors_origin_list
3. Rate limiter (slowapi) attached to app state
4. /health endpoint returns {"status": "ok"} for uptime monitoring
5. Docs disabled in production for security

Main Entry Point: app (module-level FastAPI instance)

Dependencies:
- fastapi: web framework
- slowapi: rate limiting middleware
- src.config: application settings
"""
