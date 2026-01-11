from fastapi import APIRouter
from app.controllers.health_controller import HealthController
from app.schemas.health_schema import HealthResponse, RootResponse

router = APIRouter(
    prefix="",
    tags=["Health"]
)


@router.get("/", response_model=RootResponse)
async def root():
    """
    Root endpoint - API information
    
    Returns information about the API including available endpoints
    """
    return HealthController.get_root_info()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns the current health status of the application
    """
    return HealthController.get_health_status()
