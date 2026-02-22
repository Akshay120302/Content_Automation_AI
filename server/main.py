import uvicorn
from app import app
from app.database.database import init_db
from app.database.redis_client import redis_client
from app.config import settings

# Initialize database and Redis on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    redis_client.connect()

# Cleanup on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    redis_client.disconnect()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
