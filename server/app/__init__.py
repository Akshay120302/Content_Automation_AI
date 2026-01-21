from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Content Automation AI API"
)

# Redis + Rate Limiter Init
# ------------------------
@app.on_event("startup")
async def startup():
    redis_client = redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )
    await FastAPILimiter.init(redis_client)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from app.routes import health_router
from app.routes.auth_routes import router as auth_router
from app.routes.dashboard_routes import router as dashboard_router
from app.routes.pipeline_routes import router as pipeline_router
# Import models to ensure they are registered with Base
from app.models import User, Plan, Subscription, RefreshToken, OAuthAccount

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(pipeline_router)
