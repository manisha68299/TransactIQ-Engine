"""
Core analytics engine for the E-Commerce Analytics System.
Processes transaction data using Pandas and NumPy to generate business intelligence.
This is the heart of the system - transforms raw data into actionable insights.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models import Transaction
from app.config import SUSPICIOUS_TRANSACTION_THRESHOLD
from app.utils import calculate_percentage, get_date_string, format_currency
from app.logger import logger
from datetime import datetime


class AnalyticsEngine:
    """
    Core business intelligence engine.
    Transforms raw transaction data into actionable business insights.
    Uses Pandas for data manipulation and NumPy for calculations.
    """

    @staticmethod
    def detect_suspicious_transactions(
        db: Session,
        transactions: List[Transaction]
    ) -> List[Dict[str, Any]]:
        """
        Detect suspicious transactions based on amount threshold and other heuristics.
        
        Returns list of suspicious transaction details with reasons.
        """
        suspicious_list = []
        
        for transaction in transactions:
            reason = None
            
            # Check amount threshold
            if transaction.amount > SUSPICIOUS_TRANSACTION_THRESHOLD:
                reason = f"Amount ${transaction.amount} exceeds threshold ${SUSPICIOUS_TRANSACTION_THRESHOLD}"
            
            # Check for unusual patterns (optional: multiple transactions same minute)
            if reason:
                suspicious_list.append({
                    "id": transaction.id,
                    "user_id": transaction.user_id,
                    "amount": transaction.amount,
                    "city": transaction.city,
                    "payment_method": transaction.payment_method,
                    "timestamp": transaction.timestamp,
                    "reason": reason
                })

        logger.info(f"🔍 Detected {len(suspicious_list)} suspicious transactions")
        return suspicious_list

    @staticmethod
    def calculate_revenue_metrics(transactions: List[Transaction]) -> Dict[str, float]:
        """
        Calculate comprehensive revenue analytics.
        
        Returns: total_revenue, avg_transaction, min, max, std_dev, variance
        """
        if not transactions:
            return {
                "total_revenue": 0.0,
                "transaction_count": 0,
                "average_transaction_value": 0.0,
                "min_transaction": 0.0,
                "max_transaction": 0.0,
                "standard_deviation": 0.0,
                "variance": 0.0,
                "median": 0.0
            }

        amounts = np.array([t.amount for t in transactions])

        metrics = {
            "total_revenue": float(np.sum(amounts)),
            "transaction_count": len(transactions),
            "average_transaction_value": float(np.mean(amounts)),
            "min_transaction": float(np.min(amounts)),
            "max_transaction": float(np.max(amounts)),
            "standard_deviation": float(np.std(amounts)),
            "variance": float(np.var(amounts)),
            "median": float(np.median(amounts))
        }

        logger.info(f" Revenue metrics calculated: Total=${metrics['total_revenue']:.2f}")
        return metrics

    @staticmethod
    def analyze_city_wise_revenue(transactions: List[Transaction]) -> List[Dict[str, Any]]:
        """
        Analyze revenue by city with comprehensive breakdown.
        Returns city-wise revenue breakdown with percentages and rankings.
        """
        if not transactions:
            logger.warning("No transactions for city analysis")
            return []

        try:
            df = pd.DataFrame([
                {
                    "city": t.city,
                    "amount": t.amount,
                    "user_id": t.user_id
                }
                for t in transactions
            ])

            city_analysis = df.groupby("city").agg({
                "amount": ["sum", "count", "mean"],
                "user_id": "nunique"
            }).reset_index()

            city_analysis.columns = [
                "city",
                "revenue",
                "transaction_count",
                "average_transaction",
                "unique_users"
            ]
            
            total_revenue = city_analysis["revenue"].sum()

            results = []
            for idx, row in city_analysis.iterrows():
                results.append({
                    "rank": idx + 1,
                    "city": row["city"],
                    "revenue": float(row["revenue"]),
                    "transaction_count": int(row["transaction_count"]),
                    "average_transaction": float(row["average_transaction"]),
                    "unique_users": int(row["unique_users"]),
                    "percentage_of_total": calculate_percentage(row["revenue"], total_revenue)
                })

            results = sorted(results, key=lambda x: x["revenue"], reverse=True)
            
            # Add rank
            for idx, result in enumerate(results):
                result["rank"] = idx + 1
            
            logger.info(f" City analysis completed: {len(results)} cities")
            return results
        except Exception as e:
            logger.error(f" City analysis error: {str(e)}")
            return []

    @staticmethod
    def analyze_payment_methods(transactions: List[Transaction]) -> List[Dict[str, Any]]:
        """
        Analyze transaction distribution by payment method.
        Returns payment method breakdown with percentages and statistics.
        """
        if not transactions:
            logger.warning(" No transactions for payment analysis")
            return []

        try:
            df = pd.DataFrame([
                {
                    "payment_method": t.payment_method,
                    "amount": t.amount
                }
                for t in transactions
            ])

            payment_analysis = df.groupby("payment_method").agg({
                "amount": ["sum", "count", "mean"]
            }).reset_index()

            payment_analysis.columns = [
                "payment_method",
                "total_amount",
                "transaction_count",
                "average_transaction"
            ]
            
            total_amount = payment_analysis["total_amount"].sum()
            total_transactions = payment_analysis["transaction_count"].sum()

            results = []
            for _, row in payment_analysis.iterrows():
                results.append({
                    "payment_method": row["payment_method"],
                    "transaction_count": int(row["transaction_count"]),
                    "total_amount": float(row["total_amount"]),
                    "average_transaction": float(row["average_transaction"]),
                    "percentage_of_transactions": calculate_percentage(
                        row["transaction_count"],
                        total_transactions
                    ),
                    "percentage_of_revenue": calculate_percentage(
                        row["total_amount"],
                        total_amount
                    )
                })

            results = sorted(results, key=lambda x: x["transaction_count"], reverse=True)
            logger.info(f"💳 Payment method analysis completed: {len(results)} methods")
            return results
        except Exception as e:
            logger.error(f" Payment analysis error: {str(e)}")
            return []

    @staticmethod
    def analyze_daily_trends(transactions: List[Transaction]) -> List[Dict[str, Any]]:
        """
        Analyze transaction trends by day.
        Returns daily transaction and revenue statistics with growth metrics.
        """
        if not transactions:
            logger.warning(" No transactions for trend analysis")
            return []

        try:
            df = pd.DataFrame([
                {
                    "date": get_date_string(t.timestamp),
                    "amount": t.amount
                }
                for t in transactions
            ])

            daily_analysis = df.groupby("date").agg({
                "amount": ["sum", "count", "mean", "min", "max"]
            }).reset_index()

            daily_analysis.columns = [
                "date",
                "total_revenue",
                "transaction_count",
                "average_transaction_value",
                "min_transaction",
                "max_transaction"
            ]

            # Calculate daily growth
            daily_analysis["daily_growth"] = daily_analysis["total_revenue"].pct_change() * 100

            results = []
            for _, row in daily_analysis.iterrows():
                results.append({
                    "date": row["date"],
                    "transaction_count": int(row["transaction_count"]),
                    "total_revenue": float(row["total_revenue"]),
                    "average_transaction_value": float(row["average_transaction_value"]),
                    "min_transaction": float(row["min_transaction"]),
                    "max_transaction": float(row["max_transaction"]),
                    "daily_growth_percentage": float(row["daily_growth"]) if pd.notna(row["daily_growth"]) else 0.0
                })

            results = sorted(results, key=lambda x: x["date"])
            logger.info(f" Daily trends analyzed: {len(results)} days")
            return results
        except Exception as e:
            logger.error(f" Daily trends analysis error: {str(e)}")
            return []

    @staticmethod
    def get_top_users_by_spending(
        transactions: List[Transaction],
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get top users by spending amount.
        Returns ranking of users by total spending and transaction metrics.
        """
        if not transactions:
            logger.warning(" No transactions for top users analysis")
            return []

        try:
            df = pd.DataFrame([
                {
                    "user_id": t.user_id,
                    "amount": t.amount,
                    "city": t.city
                }
                for t in transactions
            ])

            user_analysis = df.groupby("user_id").agg({
                "amount": ["sum", "count", "mean", "min", "max"],
                "city": lambda x: x.mode()[0] if len(x.mode()) > 0 else x.iloc[0]
            }).reset_index()

            user_analysis.columns = [
                "user_id",
                "total_spending",
                "transaction_count",
                "average_transaction",
                "min_transaction",
                "max_transaction",
                "primary_city"
            ]
            
            user_analysis = user_analysis.sort_values("total_spending", ascending=False).head(top_n)

            results = []
            for idx, (_, row) in enumerate(user_analysis.iterrows(), 1):
                results.append({
                    "rank": idx,
                    "user_id": row["user_id"],
                    "total_spending": float(row["total_spending"]),
                    "transaction_count": int(row["transaction_count"]),
                    "average_transaction": float(row["average_transaction"]),
                    "min_transaction": float(row["min_transaction"]),
                    "max_transaction": float(row["max_transaction"]),
                    "primary_city": row["primary_city"]
                })

            logger.info(f" Top {len(results)} users identified")
            return results
        except Exception as e:
            logger.error(f" Top users analysis error: {str(e)}")
            return []

    @staticmethod
    def get_statistical_summary(transactions: List[Transaction]) -> Dict[str, Any]:
        """
        Get comprehensive statistical summary of transactions.
        Provides percentiles, quartiles, and distribution metrics.
        """
        if not transactions:
            logger.warning(" No transactions for statistical summary")
            return {
                "total_transactions": 0,
                "total_revenue": 0.0,
                "average": 0.0,
                "median": 0.0,
                "std_dev": 0.0,
                "variance": 0.0,
                "skewness": 0.0,
                "kurtosis": 0.0,
                "percentile_25": 0.0,
                "percentile_75": 0.0,
                "percentile_95": 0.0,
                "percentile_99": 0.0,
                "min_value": 0.0,
                "max_value": 0.0,
                "range": 0.0,
                "iqr": 0.0
            }

        amounts = np.array([t.amount for t in transactions])

        percentile_25 = float(np.percentile(amounts, 25))
        percentile_75 = float(np.percentile(amounts, 75))

        summary = {
            "total_transactions": len(transactions),
            "total_revenue": float(np.sum(amounts)),
            "average": float(np.mean(amounts)),
            "median": float(np.median(amounts)),
            "std_dev": float(np.std(amounts)),
            "variance": float(np.var(amounts)),
            "skewness": float(pd.Series(amounts).skew()),
            "kurtosis": float(pd.Series(amounts).kurtosis()),
            "percentile_25": percentile_25,
            "percentile_75": percentile_75,
            "percentile_95": float(np.percentile(amounts, 95)),
            "percentile_99": float(np.percentile(amounts, 99)),
            "min_value": float(np.min(amounts)),
            "max_value": float(np.max(amounts)),
            "range": float(np.max(amounts) - np.min(amounts)),
            "iqr": percentile_75 - percentile_25
        }

        logger.info(f" Statistical summary generated for {len(transactions)} transactions")
        return summary

    @staticmethod
    def get_executive_summary(transactions: List[Transaction]) -> Dict[str, Any]:
        """
        Generate executive-level dashboard summary.
        Provides key metrics for business decision makers.
        """
        if not transactions:
            return {
                "total_revenue": 0.0,
                "total_transactions": 0,
                "average_transaction": 0.0,
                "top_city": "N/A",
                "top_payment_method": "N/A",
                "suspicious_transactions": 0,
                "total_users": 0,
                "timestamp": datetime.utcnow().isoformat()
            }

        try:
            df = pd.DataFrame([
                {
                    "user_id": t.user_id,
                    "amount": t.amount,
                    "city": t.city,
                    "payment_method": t.payment_method,
                    "is_suspicious": t.is_suspicious
                }
                for t in transactions
            ])

            total_revenue = df["amount"].sum()
            total_transactions = len(df)
            average_transaction = df["amount"].mean()
            top_city = df["city"].mode()[0] if len(df["city"].mode()) > 0 else "N/A"
            top_payment = df["payment_method"].mode()[0] if len(df["payment_method"].mode()) > 0 else "N/A"
            suspicious = df["is_suspicious"].sum()
            unique_users = df["user_id"].nunique()

            summary = {
                "total_revenue": float(total_revenue),
                "total_transactions": int(total_transactions),
                "average_transaction": float(average_transaction),
                "top_city": str(top_city),
                "top_payment_method": str(top_payment),
                "suspicious_transactions": int(suspicious),
                "total_users": int(unique_users),
                "timestamp": datetime.utcnow().isoformat()
            }

            logger.info(" Executive summary generated")
            return summary
        except Exception as e:
            logger.error(f" Executive summary error: {str(e)}")
            return {}