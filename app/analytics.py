"""
Core analytics engine for the E-Commerce Analytics System.
Processes transaction data using Pandas and NumPy to generate business intelligence.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models import Transaction
from app.config import SUSPICIOUS_TRANSACTION_THRESHOLD
from app.utils import calculate_percentage, get_date_string
from app.logger import log_analytics_generated, log_error
from datetime import datetime


class AnalyticsEngine:
    """
    Core business intelligence engine.
    Transforms raw transaction data into actionable business insights.
    """

    @staticmethod
    def detect_suspicious_transactions(db: Session, transactions: List[Transaction]) -> List[int]:
        """
        Detect suspicious transactions based on amount threshold.
        Returns list of suspicious transaction IDs.
        """
        suspicious_ids = []
        for transaction in transactions:
            if transaction.amount > SUSPICIOUS_TRANSACTION_THRESHOLD:
                suspicious_ids.append(transaction.id)

        log_analytics_generated("suspicious_transaction_detection", len(suspicious_ids))
        return suspicious_ids

    @staticmethod
    def calculate_revenue_metrics(transactions: List[Transaction]) -> Dict[str, float]:
        """
        Calculate revenue analytics.
        Returns: total_revenue, avg_transaction, min, max, std_dev
        """
        if not transactions:
            return {
                "total_revenue": 0.0,
                "transaction_count": 0,
                "average_transaction_value": 0.0,
                "min_transaction": 0.0,
                "max_transaction": 0.0,
                "standard_deviation": 0.0
            }

        amounts = np.array([t.amount for t in transactions])

        metrics = {
            "total_revenue": float(np.sum(amounts)),
            "transaction_count": len(transactions),
            "average_transaction_value": float(np.mean(amounts)),
            "min_transaction": float(np.min(amounts)),
            "max_transaction": float(np.max(amounts)),
            "standard_deviation": float(np.std(amounts))
        }

        log_analytics_generated("revenue_metrics", len(transactions))
        return metrics

    @staticmethod
    def analyze_city_wise_revenue(transactions: List[Transaction]) -> List[Dict[str, Any]]:
        """
        Analyze revenue by city.
        Returns city-wise revenue breakdown with percentages.
        """
        if not transactions:
            return []

        df = pd.DataFrame([
            {
                "city": t.city,
                "amount": t.amount
            }
            for t in transactions
        ])

        city_analysis = df.groupby("city").agg({
            "amount": ["sum", "count"]
        }).reset_index()

        city_analysis.columns = ["city", "revenue", "transaction_count"]
        total_revenue = city_analysis["revenue"].sum()

        results = []
        for _, row in city_analysis.iterrows():
            results.append({
                "city": row["city"],
                "revenue": float(row["revenue"]),
                "transaction_count": int(row["transaction_count"]),
                "percentage_of_total": calculate_percentage(row["revenue"], total_revenue)
            })

        results = sorted(results, key=lambda x: x["revenue"], reverse=True)
        log_analytics_generated("city_wise_analysis", len(results))
        return results

    @staticmethod
    def analyze_payment_methods(transactions: List[Transaction]) -> List[Dict[str, Any]]:
        """
        Analyze transaction distribution by payment method.
        Returns payment method breakdown with percentages.
        """
        if not transactions:
            return []

        df = pd.DataFrame([
            {
                "payment_method": t.payment_method,
                "amount": t.amount
            }
            for t in transactions
        ])

        payment_analysis = df.groupby("payment_method").agg({
            "amount": ["sum", "count"]
        }).reset_index()

        payment_analysis.columns = ["payment_method", "total_amount", "transaction_count"]
        total_amount = payment_analysis["total_amount"].sum()

        results = []
        for _, row in payment_analysis.iterrows():
            results.append({
                "payment_method": row["payment_method"],
                "transaction_count": int(row["transaction_count"]),
                "total_amount": float(row["total_amount"]),
                "percentage_of_total": calculate_percentage(row["transaction_count"], len(transactions))
            })

        results = sorted(results, key=lambda x: x["transaction_count"], reverse=True)
        log_analytics_generated("payment_method_analysis", len(results))
        return results

    @staticmethod
    def analyze_daily_trends(transactions: List[Transaction]) -> List[Dict[str, Any]]:
        """
        Analyze transaction trends by day.
        Returns daily transaction and revenue statistics.
        """
        if not transactions:
            return []

        df = pd.DataFrame([
            {
                "date": get_date_string(t.timestamp),
                "amount": t.amount
            }
            for t in transactions
        ])

        daily_analysis = df.groupby("date").agg({
            "amount": ["sum", "count", "mean"]
        }).reset_index()

        daily_analysis.columns = ["date", "total_revenue", "transaction_count", "average_transaction_value"]

        results = []
        for _, row in daily_analysis.iterrows():
            results.append({
                "date": row["date"],
                "transaction_count": int(row["transaction_count"]),
                "total_revenue": float(row["total_revenue"]),
                "average_transaction_value": float(row["average_transaction_value"])
            })

        results = sorted(results, key=lambda x: x["date"])
        log_analytics_generated("daily_trends_analysis", len(results))
        return results

    @staticmethod
    def get_top_users_by_spending(transactions: List[Transaction], top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Get top users by spending amount.
        """
        if not transactions:
            return []

        df = pd.DataFrame([
            {
                "user_id": t.user_id,
                "amount": t.amount
            }
            for t in transactions
        ])

        user_analysis = df.groupby("user_id").agg({
            "amount": ["sum", "count"]
        }).reset_index()

        user_analysis.columns = ["user_id", "total_spending", "transaction_count"]
        user_analysis = user_analysis.sort_values("total_spending", ascending=False).head(top_n)

        results = []
        for _, row in user_analysis.iterrows():
            results.append({
                "user_id": row["user_id"],
                "total_spending": float(row["total_spending"]),
                "transaction_count": int(row["transaction_count"]),
                "average_transaction": float(row["total_spending"] / row["transaction_count"])
            })

        log_analytics_generated("top_users_analysis", len(results))
        return results

    @staticmethod
    def get_statistical_summary(transactions: List[Transaction]) -> Dict[str, Any]:
        """
        Get comprehensive statistical summary of transactions.
        """
        if not transactions:
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

        amounts = np.array([t.amount for t in transactions])

        return {
            "total_transactions": len(transactions),
            "total_revenue": float(np.sum(amounts)),
            "average": float(np.mean(amounts)),
            "median": float(np.median(amounts)),
            "std_dev": float(np.std(amounts)),
            "percentile_25": float(np.percentile(amounts, 25)),
            "percentile_75": float(np.percentile(amounts, 75)),
            "percentile_95": float(np.percentile(amounts, 95))
        }
