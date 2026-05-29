"""
Main entry point of the E-Commerce Analytics Engine.
Initializes FastAPI application, connects routes, starts server.
Production-ready with comprehensive error handling and middleware.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.database import init_db
from app.routes import transaction_routes, analytics_routes, upload_routes
from app.config import API_TITLE, API_VERSION, API_DESCRIPTION, ALLOWED_HOSTS
from app.logger import logger

# Initialize database
init_db()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle events."""
    # Startup
    logger.info("=" * 80)
    logger.info("Real-Time E-Commerce Analytics Engine Starting...")
    logger.info("Backend Intelligence System Initialized")
    logger.info("=" * 80)
    yield
    # Shutdown
    logger.info(" Application Shutdown - Cleaning Up Resources")


# Create FastAPI app with lifespan context manager
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Add security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=ALLOWED_HOSTS
)

# Add CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle uncaught exceptions globally."""
    logger.log_error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "detail": str(exc)
        }
    )


# Include routes
app.include_router(transaction_routes.router, prefix="/api", tags=["Transactions"])
app.include_router(analytics_routes.router, prefix="/api", tags=["Analytics"])
app.include_router(upload_routes.router, prefix="/api", tags=["Upload"])


# Health check endpoint
@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Real-Time E-Commerce Analytics Engine",
        "version": API_VERSION,
        "message": "Backend intelligence system is running",
        "timestamp": logger.format_date(logger.datetime.datetime.utcnow())
    }


# API Documentation Summary
@app.get("/docs-summary", tags=["Documentation"])
def api_summary():
    """Complete API documentation and summary."""
    return {
        "api_name": API_TITLE,
        "version": API_VERSION,
        "description": API_DESCRIPTION,
        "base_url": "/api",
        "endpoints": {
            "transactions": {
                "POST /transactions": "Submit a new transaction",
                "GET /transactions": "Retrieve all transactions with pagination",
                "GET /transactions/{transaction_id}": "Get a specific transaction",
                "GET /transactions/by-city/{city}": "Get transactions by city",
                "GET /transactions/by-user/{user_id}": "Get transactions by user",
                "GET /transactions/suspicious/all": "Get all suspicious transactions"
            },
            "analytics": {
                "GET /analytics/revenue": "Revenue analytics report",
                "GET /analytics/top-cities": "City-wise revenue breakdown",
                "GET /analytics/payment-analysis": "Payment method analysis",
                "GET /analytics/daily-trends": "Daily transaction trends",
                "GET /analytics/top-users": "Top users by spending",
                "GET /analytics/statistics": "Statistical summary",
                "GET /analytics/summary": "Executive summary dashboard"
            },
            "upload": {
                "POST /upload/csv": "Upload CSV for bulk transaction processing"
            }
        },
        "features": [
            "Real-time transaction processing",
            "Advanced business analytics generation",
            "Suspicious transaction detection",
            "City-wise revenue analysis",
            "Payment method distribution",
            "Daily trend analysis",
            "Statistical reporting",
            "CSV bulk import",
            "Top customers identification",
            "Comprehensive logging"
        ],
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )