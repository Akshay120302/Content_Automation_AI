from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Content Automation AI API"
)

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
# Import models to ensure they are registered with Base
from app.models import User, Plan, Subscription, RefreshToken, OAuthAccount

app.include_router(health_router)
app.include_router(auth_router)
