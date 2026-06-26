import json
from sqlalchemy.orm import Session
from database.models import AuditLog, AgentActionTrace

def log_action(db: Session, system_id: str, user: str, action: str, details: dict):
    """Logs an action to the audit trail."""
    new_log = AuditLog(
        system_id=system_id,
        user=user,
        action=action,
        details=json.dumps(details)
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log

def get_audit_logs(db: Session, system_id: str):
    """Retrieves all audit logs for a specific system."""
    return db.query(AuditLog).filter(AuditLog.system_id == system_id).order_by(AuditLog.timestamp.desc()).all()

def log_agent_trace(db: Session, audit_log_id: str, step_number: int, action_taken: str, tool_used: str, decision_rationale: str):
    """Logs a single step of an agentic action trace."""
    new_trace = AgentActionTrace(
        audit_log_id=audit_log_id,
        step_number=step_number,
        action_taken=action_taken,
        tool_used=tool_used,
        decision_rationale=decision_rationale
    )
    db.add(new_trace)
    db.commit()
    db.refresh(new_trace)
    return new_trace
