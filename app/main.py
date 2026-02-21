from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router
from app.core.config import settings

def create_app() -> FastAPI:
    """
    Factory function to initialize the FastAPI application.
    This allows for better testing and modularity.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="Microservice for converting agricultural field voice records to text.",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routes
    app.include_router(api_router)

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app", 
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
