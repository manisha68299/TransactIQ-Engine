"""
Analytics API routes.
Exposes business insights and analytical reports through REST APIs.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import (
    RevenueAnalyticsResponse,
    CityAnalyticsResponse,
    PaymentAnalyticsResponse,
    DailyTrendResponse
)
from app.crud import get_all_transactions_for_analytics
from app.analytics import AnalyticsEngine
from app.logger import log_error, log_api_request

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/revenue", response_model=RevenueAnalyticsResponse)
def get_revenue_analytics(db: Session = Depends(get_db)):
    """
    Get comprehensive revenue analytics.
    Returns: total revenue, transaction count, averages, min/max, standard deviation.
    """
    try:
        transactions = get_all_transactions_for_analytics(db)

        if not transactions:
            log_api_request("GET", "/analytics/revenue", 200)
            return {
                "total_revenue": 0.0,
                "transaction_count": 0,
                "average_transaction_value": 0.0,
                "min_transaction": 0.0,
                "max_transaction": 0.0,
                "standard_deviation": 0.0
            }

        metrics = AnalyticsEngine.calculate_revenue_metrics(transactions)
        log_api_request("GET", "/analytics/revenue", 200)
        return metrics
    except Exception as e:
        log_error(str(e), "get_revenue_analytics")
        raise HTTPException(status_code=500, detail="Error generating revenue analytics")


@router.get("/top-cities", response_model=List[CityAnalyticsResponse])
def get_city_analytics(db: Session = Depends(get_db)):
    """
    Get city-wise revenue breakdown.
    Returns top cities by revenue with percentages.
    """
    try:
        transactions = get_all_transactions_for_analytics(db)

        if not transactions:
            log_api_request("GET", "/analytics/top-cities", 200)
            return []

        city_analysis = AnalyticsEngine.analyze_city_wise_revenue(transactions)
        log_api_request("GET", "/analytics/top-cities", 200)
        return city_analysis
    except Exception as e:
        log_error(str(e), "get_city_analytics")
        raise HTTPException(status_code=500, detail="Error generating city analytics")


@router.get("/payment-analysis", response_model=List[PaymentAnalyticsResponse])
def get_payment_analytics(db: Session = Depends(get_db)):
    """
    Get payment method distribution analysis.
    Returns breakdown by payment method with counts and percentages.
    """
    try:
        transactions = get_all_transactions_for_analytics(db)

        if not transactions:
            log_api_request("GET", "/analytics/payment-analysis", 200)
            return []

        payment_analysis = AnalyticsEngine.analyze_payment_methods(transactions)
        log_api_request("GET", "/analytics/payment-analysis", 200)
        return payment_analysis
    except Exception as e:
        log_error(str(e), "get_payment_analytics")
        raise HTTPException(status_code=500, detail="Error generating payment analytics")


@router.get("/daily-trends", response_model=List[DailyTrendResponse])
def get_daily_trends(db: Session = Depends(get_db)):
    """
    Get daily transaction trends.
    Returns daily aggregated metrics: transaction count, revenue, averages.
    """
    try:
        transactions = get_all_transactions_for_analytics(db)

        if not transactions:
            log_api_request("GET", "/analytics/daily-trends", 200)
            return []

        trends = AnalyticsEngine.analyze_daily_trends(transactions)
        log_api_request("GET", "/analytics/daily-trends", 200)
        return trends
    except Exception as e:
        log_error(str(e), "get_daily_trends")
        raise HTTPException(status_code=500, detail="Error generating daily trends")


@router.get("/top-users")
def get_top_users(db: Session = Depends(get_db), limit: int = 10):
    """
    Get top users by spending amount.
    """
    try:
        transactions = get_all_transactions_for_analytics(db)

        if not transactions:
            log_api_request("GET", "/analytics/top-users", 200)
            return []

        top_users = AnalyticsEngine.get_top_users_by_spending(transactions, top_n=limit)
        log_api_request("GET", "/analytics/top-users", 200)
        return top_users
    except Exception as e:
        log_error(str(e), "get_top_users")
        raise HTTPException(status_code=500, detail="Error generating top users report")


@router.get("/statistics")
def get_statistics(db: Session = Depends(get_db)):
    """
    Get comprehensive statistical summary.
    Returns percentiles, median, mean, std deviation, etc.
    """
    try:
        transactions = get_all_transactions_for_analytics(db)

        if not transactions:
            log_api_request("GET", "/analytics/statistics", 200)
            return {
                "total_transactions": 0,
                "total_revenue": 0.0,
                "average": 0.0,
                "median": 0.0,
                "std_dev": 0.0,
                "percentile_25": 0.0,
                "percentile_75": 0.0,
                "percentile_95": 0.0
            }

        stats = AnalyticsEngine.get_statistical_summary(transactions)
        log_api_request("GET", "/analytics/statistics", 200)
        return stats
    except Exception as e:
        log_error(str(e), "get_statistics")
        raise HTTPException(status_code=500, detail="Error generating statistics")
