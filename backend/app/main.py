from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.routes.image import router as image_router
from app.routes.search import router as search_router
from app.routes.auth import router as auth_router
from app.routes.dashboard import router as dashboard_router
from app.database import create_tables, test_database_connection
from app.config import settings
import logging
import os
import uvicorn

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Search & Image API", 
    version="1.0.0",
    debug=settings.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting up Search & Image API...")
    
    # Test database connection
    if not test_database_connection():
        logger.error("Failed to connect to database")
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    # Create database tables (only if they don't exist)
    if not create_tables():
        logger.error("Failed to create database tables")
        raise HTTPException(status_code=500, detail="Database initialization failed")
    
    logger.info("Application startup completed successfully!")

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(image_router, prefix="/images", tags=["images"])
app.include_router(search_router, prefix="/search", tags=["search"])
app.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])

@app.get("/")
def read_root():
    return {"message": "Search & Image API is running!", "version": "1.0.0"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Render sets PORT automatically
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
