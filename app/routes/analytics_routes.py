"""
API routes for analytics and business intelligence.
Exposes analytics reports and business insights through REST APIs.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud import get_all_transactions_for_analytics
from app.analytics import AnalyticsEngine
from app.schemas import (
    RevenueAnalyticsResponse,
    CityAnalyticsListResponse,
    PaymentAnalyticsListResponse,
    DailyTrendsListResponse,
    TopUsersListResponse,
    StatisticalSummaryResponse,
    SuspiciousTransactionListResponse,
    ExecutiveSummaryResponse
)
from app.logger import logger

router = APIRouter()


@router.get("/analytics/revenue", response_model=RevenueAnalyticsResponse)
async def get_revenue_analytics(db: Session = Depends(get_db)):
    """
    Get revenue analytics report.
    
    Returns:
    - Total revenue
    - Transaction count
    - Average transaction value
    - Min/Max transaction
    - Standard deviation
    """
    try:
        transactions = get_all_transactions_for_analytics(db)
        metrics = AnalyticsEngine.calculate_revenue_metrics(transactions)
        
        logger.log_analytics_generated("revenue_analytics", len(transactions))
        logger.log_api_request("GET", "/analytics/revenue", 200)
        
        return metrics
    except Exception as e:
        logger.error(str(e), "get_revenue_analytics")
        raise HTTPException(status_code=500, detail="Failed to generate revenue analytics")


@router.get("/analytics/top-cities", response_model=CityAnalyticsListResponse)
async def get_city_analytics(db: Session = Depends(get_db)):
    """
    Get city-wise revenue breakdown.
    
    Returns:
    - Revenue by city
    - Transaction count per city
    - Percentage of total revenue
    - Average transaction per city
    """
    try:
        transactions = get_all_transactions_for_analytics(db)
        city_data = AnalyticsEngine.analyze_city_wise_revenue(transactions)
        
        total_revenue = sum(city["revenue"] for city in city_data)
        
        logger.log_analytics_generated("city_analytics", len(city_data))
        logger.log_api_request("GET", "/analytics/top-cities", 200)
        
        return CityAnalyticsListResponse(
            total_cities=len(city_data),
            total_revenue=total_revenue,
            data=city_data
        )
    except Exception as e:
        logger.error(str(e), "get_city_analytics")
        raise HTTPException(status_code=500, detail="Failed to generate city analytics")


@router.get("/analytics/payment-analysis", response_model=PaymentAnalyticsListResponse)
async def get_payment_analytics(db: Session = Depends(get_db)):
    """
    Get payment method analysis.
    
    Returns:
    - Transaction count by payment method
    - Total amount by payment method
    - Percentage distribution
    """
    try:
        transactions = get_all_transactions_for_analytics(db)
        payment_data = AnalyticsEngine.analyze_payment_methods(transactions)
        
        total_transactions = sum(p["transaction_count"] for p in payment_data)
        
        logger.log_analytics_generated("payment_analytics", len(payment_data))
        logger.log_api_request("GET", "/analytics/payment-analysis", 200)
        
        return PaymentAnalyticsListResponse(
            payment_methods=len(payment_data),
            total_transactions=total_transactions,
            data=payment_data
        )
    except Exception as e:
        logger.error(str(e), "get_payment_analytics")
        raise HTTPException(status_code=500, detail="Failed to generate payment analytics")


@router.get("/analytics/daily-trends", response_model=DailyTrendsListResponse)
async def get_daily_trends(db: Session = Depends(get_db)):
    """
    Get daily transaction trends.
    
    Returns:
    - Daily revenue
    - Daily transaction count
    - Average transaction value per day
    - Daily growth percentage
    """
    try:
        transactions = get_all_transactions_for_analytics(db)
        trends_data = AnalyticsEngine.analyze_daily_trends(transactions)
        
        total_revenue = sum(t["total_revenue"] for t in trends_data)
        total_transactions = sum(t["transaction_count"] for t in trends_data)
        
        logger.log_analytics_generated("daily_trends", len(trends_data))
        logger.log_api_request("GET", "/analytics/daily-trends", 200)
        
        return DailyTrendsListResponse(
            total_days=len(trends_data),
            total_revenue=total_revenue,
            total_transactions=total_transactions,
            data=trends_data
        )
    except Exception as e:
        logger.error(str(e), "get_daily_trends")
        raise HTTPException(status_code=500, detail="Failed to generate daily trends")


@router.get("/analytics/top-users", response_model=TopUsersListResponse)
async def get_top_users(
    top_n: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get top users by spending.
    
    Parameters:
    - top_n: Number of top users to return (default: 10, max: 100)
    
    Returns:
    - User ID
    - Total spending
    - Transaction count
    - Average transaction
    - Primary city
    """
    try:
        transactions = get_all_transactions_for_analytics(db)
        users_data = AnalyticsEngine.get_top_users_by_spending(transactions, top_n=top_n)
        
        logger.log_analytics_generated("top_users", len(users_data))
        logger.log_api_request("GET", f"/analytics/top-users?top_n={top_n}", 200)
        
        return TopUsersListResponse(
            total_users=len(users_data),
            data=users_data
        )
    except Exception as e:
        logger.error(str(e), "get_top_users")
        raise HTTPException(status_code=500, detail="Failed to generate top users analytics")


@router.get("/analytics/statistics", response_model=StatisticalSummaryResponse)
async def get_statistics(db: Session = Depends(get_db)):
    """
    Get comprehensive statistical summary.
    
    Returns:
    - Mean, median, standard deviation
    - Quartiles and percentiles
    - Min/Max values
    - Range and IQR
    """
    try:
        transactions = get_all_transactions_for_analytics(db)
        stats = AnalyticsEngine.get_statistical_summary(transactions)
        
        logger.log_analytics_generated("statistics", len(transactions))
        logger.log_api_request("GET", "/analytics/statistics", 200)
        
        return stats
    except Exception as e:
        logger.error(str(e), "get_statistics")
        raise HTTPException(status_code=500, detail="Failed to generate statistics")


@router.get("/analytics/suspicious-transactions", response_model=SuspiciousTransactionListResponse)
async def get_suspicious_analytics(db: Session = Depends(get_db)):
    """
    Get suspicious transactions with reasons.
    
    Returns:
    - List of suspicious transactions
    - Reason for flagging
    - Total flagged amount
    """
    try:
        transactions = get_all_transactions_for_analytics(db)
        suspicious_data = AnalyticsEngine.detect_suspicious_transactions(db, transactions)
        
        total_flagged = sum(t["amount"] for t in suspicious_data)
        
        logger.log_analytics_generated("suspicious_transactions", len(suspicious_data))
        logger.log_api_request("GET", "/analytics/suspicious-transactions", 200)
        
        return SuspiciousTransactionListResponse(
            total_suspicious=len(suspicious_data),
            total_amount_flagged=total_flagged,
            data=suspicious_data
        )
    except Exception as e:
        logger.error(str(e), "get_suspicious_analytics")
        raise HTTPException(status_code=500, detail="Failed to generate suspicious analytics")


@router.get("/analytics/summary", response_model=ExecutiveSummaryResponse)
async def get_executive_summary(db: Session = Depends(get_db)):
    """
    Get executive summary dashboard.
    
    High-level metrics for business decision makers:
    - Total revenue
    - Total transactions
    - Average transaction
    - Top city
    - Top payment method
    - Suspicious transaction count
    - Total unique users
    """
    try:
        transactions = get_all_transactions_for_analytics(db)
        summary = AnalyticsEngine.get_executive_summary(transactions)
        
        logger.log_analytics_generated("executive_summary", len(transactions))
        logger.log_api_request("GET", "/analytics/summary", 200)
        
        return summary
    except Exception as e:
        logger.error(str(e), "get_executive_summary")
        raise HTTPException(status_code=500, detail="Failed to generate executive summary")