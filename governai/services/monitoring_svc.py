from sqlalchemy.orm import Session
from database.models import MonitoringMetric, AISystem
from services.ai_system_svc import update_status
from services.audit_svc import log_action

DEFAULT_THRESHOLDS = {
    "Drift": 0.15,
    "Bias": 0.1,
    "Hallucination": 0.05,
    "Cost": 1000.0
}

def ingest_metric(db: Session, system_id: str, metric_name: str, metric_value: float, current_user: str):
    """Ingests a new metric reading, checks against thresholds, and updates state if breached."""
    threshold = DEFAULT_THRESHOLDS.get(metric_name, 0.0)
    is_breached = 1 if metric_value > threshold else 0
    
    # 1. Save Metric
    new_metric = MonitoringMetric(
        system_id=system_id,
        metric_name=metric_name,
        metric_value=metric_value,
        threshold_value=threshold,
        is_breached=is_breached
    )
    db.add(new_metric)
    db.commit()
    db.refresh(new_metric)
    
    # 2. Trigger Cross-Wiring (The Golden Thread)
    if is_breached:
        system = db.query(AISystem).filter(AISystem.id == system_id).first()
        
        # Only log and update if we aren't already non-compliant
        if system and system.compliance_status != "Non-Compliant":
            reason = f"{metric_name} exceeded threshold: {metric_value} > {threshold}"
            
            # Log specific breach action
            log_action(db, system_id, "System Engine", "METRIC_BREACH", {
                "metric_name": metric_name,
                "metric_value": metric_value,
                "threshold": threshold,
                "triggering_user": current_user
            })
            
            # Update status
            update_status(db, system_id, "Non-Compliant", "System Engine", reason=reason)
            
    return new_metric

def get_metrics(db: Session, system_id: str, limit: int = 50):
    """Retrieves recent metrics for a system."""
    return db.query(MonitoringMetric).filter(MonitoringMetric.system_id == system_id).order_by(MonitoringMetric.timestamp.desc()).limit(limit).all()
