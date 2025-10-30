"""
Drift Monitoring and Alerting System
Tracks Trust Score changes over time and triggers alerts
"""
import os
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from cee_pipeline.database.models import DriftMetric, DriftAlertDB, TrustScoreDB, Evaluation
from cee_pipeline.models.schemas import DriftAlert


class DriftMonitor:
    """
    Post-deployment monitoring that tracks Trust Score over time.
    Alerts when scores deviate beyond thresholds.
    """

    def __init__(
        self,
        absolute_threshold: float = None,
        relative_threshold: float = None
    ):
        """
        Initialize Drift Monitor

        Args:
            absolute_threshold: Absolute change threshold (default from env or 5.0)
            relative_threshold: Relative change threshold (default from env or 0.10 = 10%)
        """
        self.absolute_threshold = absolute_threshold or float(
            os.getenv("DRIFT_THRESHOLD_ABSOLUTE", "5.0")
        )
        self.relative_threshold = relative_threshold or float(
            os.getenv("DRIFT_THRESHOLD_RELATIVE", "0.10")
        )

    def record_metric(
        self,
        db: Session,
        metric_name: str,
        metric_value: float,
        model_name: str = None,
        dataset_name: str = None,
        baseline_value: float = None
    ):
        """
        Record a metric for drift monitoring

        Args:
            db: Database session
            metric_name: Name of metric (e.g., "trust_score", "tier1_pass_rate")
            metric_value: Current value
            model_name: Optional model name
            dataset_name: Optional dataset name
            baseline_value: Optional baseline for comparison
        """
        metric = DriftMetric(
            metric_name=metric_name,
            metric_value=metric_value,
            baseline_value=baseline_value,
            model_name=model_name,
            dataset_name=dataset_name,
            recorded_at=datetime.utcnow()
        )
        db.add(metric)
        db.commit()

    def calculate_baseline(
        self,
        db: Session,
        metric_name: str,
        lookback_days: int = 7,
        model_name: str = None,
        dataset_name: str = None
    ) -> Optional[float]:
        """
        Calculate baseline value for a metric

        Args:
            db: Database session
            metric_name: Name of metric
            lookback_days: Days to look back for baseline
            model_name: Optional model filter
            dataset_name: Optional dataset filter

        Returns:
            Average metric value or None
        """
        cutoff_date = datetime.utcnow() - timedelta(days=lookback_days)

        query = db.query(func.avg(DriftMetric.metric_value)).filter(
            and_(
                DriftMetric.metric_name == metric_name,
                DriftMetric.recorded_at >= cutoff_date
            )
        )

        if model_name:
            query = query.filter(DriftMetric.model_name == model_name)
        if dataset_name:
            query = query.filter(DriftMetric.dataset_name == dataset_name)

        baseline = query.scalar()
        return float(baseline) if baseline else None

    def check_drift(
        self,
        db: Session,
        metric_name: str,
        current_value: float,
        model_name: str = None,
        dataset_name: str = None
    ) -> Optional[DriftAlert]:
        """
        Check if current value has drifted from baseline

        Args:
            db: Database session
            metric_name: Name of metric
            current_value: Current metric value
            model_name: Optional model filter
            dataset_name: Optional dataset filter

        Returns:
            DriftAlert if drift detected, None otherwise
        """
        # Get baseline
        baseline = self.calculate_baseline(
            db, metric_name,
            model_name=model_name,
            dataset_name=dataset_name
        )

        if baseline is None:
            return None  # Not enough data for baseline

        # Calculate changes
        absolute_change = abs(current_value - baseline)
        relative_change = absolute_change / baseline if baseline != 0 else 0

        # Check thresholds
        if absolute_change < self.absolute_threshold and relative_change < self.relative_threshold:
            return None  # No significant drift

        # Determine severity
        severity = "warning"
        if absolute_change >= self.absolute_threshold * 2 or relative_change >= self.relative_threshold * 2:
            severity = "critical"

        # Create alert
        alert_id = str(uuid.uuid4())
        message = (
            f"Drift detected for {metric_name}: "
            f"current={current_value:.2f}, baseline={baseline:.2f}, "
            f"change={absolute_change:.2f} ({relative_change*100:.1f}%)"
        )

        alert = DriftAlert(
            alert_id=alert_id,
            metric_name=metric_name,
            current_value=current_value,
            baseline_value=baseline,
            absolute_change=absolute_change,
            relative_change=relative_change,
            severity=severity,
            triggered_at=datetime.utcnow(),
            message=message
        )

        # Save to database
        db_alert = DriftAlertDB(
            id=alert_id,
            metric_name=metric_name,
            current_value=current_value,
            baseline_value=baseline,
            absolute_change=absolute_change,
            relative_change=relative_change,
            severity=severity,
            message=message,
            triggered_at=datetime.utcnow()
        )
        db.add(db_alert)
        db.commit()

        return alert

    def calculate_drift_stability_index(
        self,
        db: Session,
        metric_name: str,
        lookback_days: int = 30,
        model_name: str = None
    ) -> float:
        """
        Calculate Drift Stability Index (DSI)
        Combines absolute and relative performance changes

        Args:
            db: Database session
            metric_name: Name of metric
            lookback_days: Days to analyze
            model_name: Optional model filter

        Returns:
            DSI score (0-100, higher is more stable)
        """
        cutoff_date = datetime.utcnow() - timedelta(days=lookback_days)

        query = db.query(DriftMetric.metric_value).filter(
            and_(
                DriftMetric.metric_name == metric_name,
                DriftMetric.recorded_at >= cutoff_date
            )
        ).order_by(DriftMetric.recorded_at)

        if model_name:
            query = query.filter(DriftMetric.model_name == model_name)

        values = [v[0] for v in query.all()]

        if len(values) < 2:
            return 100.0  # Perfect stability (insufficient data)

        # Calculate coefficient of variation
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        cv = (std_dev / mean) if mean != 0 else 0

        # Convert to stability score (lower CV = higher stability)
        # DSI = 100 * e^(-cv)
        import math
        dsi = 100.0 * math.exp(-cv)

        return round(dsi, 2)

    def get_recent_alerts(
        self,
        db: Session,
        hours: int = 24,
        severity: str = None
    ) -> List[Dict]:
        """
        Get recent drift alerts

        Args:
            db: Database session
            hours: Hours to look back
            severity: Optional severity filter

        Returns:
            List of alert dictionaries
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        query = db.query(DriftAlertDB).filter(
            DriftAlertDB.triggered_at >= cutoff_time
        ).order_by(DriftAlertDB.triggered_at.desc())

        if severity:
            query = query.filter(DriftAlertDB.severity == severity)

        alerts = query.all()

        return [
            {
                'alert_id': alert.id,
                'metric_name': alert.metric_name,
                'current_value': alert.current_value,
                'baseline_value': alert.baseline_value,
                'absolute_change': alert.absolute_change,
                'relative_change': alert.relative_change,
                'severity': alert.severity,
                'message': alert.message,
                'triggered_at': alert.triggered_at.isoformat(),
                'acknowledged': alert.acknowledged
            }
            for alert in alerts
        ]

    def acknowledge_alert(self, db: Session, alert_id: str):
        """Mark an alert as acknowledged"""
        alert = db.query(DriftAlertDB).filter(DriftAlertDB.id == alert_id).first()
        if alert:
            alert.acknowledged = True
            alert.acknowledged_at = datetime.utcnow()
            db.commit()

    def get_dashboard_metrics(self, db: Session, hours: int = 24) -> Dict:
        """
        Get aggregated metrics for dashboard

        Args:
            db: Database session
            hours: Hours to look back

        Returns:
            Dictionary with dashboard metrics
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        # Total evaluations
        total_evals = db.query(func.count(Evaluation.id)).filter(
            Evaluation.created_at >= cutoff_time
        ).scalar() or 0

        # Average trust score
        avg_trust = db.query(func.avg(TrustScoreDB.overall)).join(
            Evaluation
        ).filter(
            Evaluation.created_at >= cutoff_time
        ).scalar() or 0

        # Get recent alerts
        recent_alerts = self.get_recent_alerts(db, hours=hours)

        return {
            'total_evaluations': total_evals,
            'average_trust_score': round(float(avg_trust), 2) if avg_trust else 0,
            'recent_alerts_count': len(recent_alerts),
            'critical_alerts_count': sum(1 for a in recent_alerts if a['severity'] == 'critical')
        }
