"""
Main entry point of the E-Commerce Analytics Engine.
Initializes FastAPI application, connects routes, starts server.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routes import transaction_routes, analytics_routes, upload_routes
from app.config import API_TITLE, API_VERSION, API_DESCRIPTION
from app.logger import logger

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routes
app.include_router(transaction_routes.router)
app.include_router(analytics_routes.router)
app.include_router(upload_routes.router)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("🚀 Real-Time E-Commerce Analytics Engine Starting...")
    logger.info("📊 Backend Intelligence System Initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("🛑 Application Shutdown")


@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Real-Time E-Commerce Analytics Engine",
        "version": API_VERSION,
        "message": "Backend intelligence system is running"
    }


@app.get("/docs-summary", tags=["Documentation"])
def api_summary():
    """API Documentation Summary."""
    return {
        "api_name": API_TITLE,
        "version": API_VERSION,
        "endpoints": {
            "transactions": {
                "POST /transactions": "Submit a new transaction",
                "GET /transactions": "Retrieve all transactions",
                "GET /transactions/by-city/{city}": "Get transactions by city",
                "GET /transactions/suspicious/all": "Get suspicious transactions"
            },
            "analytics": {
                "GET /analytics/revenue": "Revenue analytics report",
                "GET /analytics/top-cities": "City-wise revenue breakdown",
                "GET /analytics/payment-analysis": "Payment method analysis",
                "GET /analytics/daily-trends": "Daily transaction trends",
                "GET /analytics/top-users": "Top users by spending",
                "GET /analytics/statistics": "Statistical summary"
            },
            "upload": {
                "POST /upload/csv": "Upload CSV for bulk transaction processing"
            }
        },
        "features": [
            "Real-time transaction processing",
            "Business analytics generation",
            "Suspicious transaction detection",
            "City-wise revenue analysis",
            "Payment method distribution",
            "Daily trend analysis",
            "Statistical reporting",
            "CSV bulk import"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
