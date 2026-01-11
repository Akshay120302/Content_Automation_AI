import uvicorn
from app import app
from app.database.database import init_db
from app.config import settings

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
