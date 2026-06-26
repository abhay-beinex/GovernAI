from sqlalchemy.orm import Session
from database.models import AISystem, DataSource
from services.audit_svc import log_action

def create_system(db: Session, system_data: dict, current_user: str):
    """Creates a new AI system and logs the creation."""
    new_system = AISystem(
        name=system_data.get("name"),
        owner=system_data.get("owner"),
        business_purpose=system_data.get("business_purpose"),
        model_vendor=system_data.get("model_vendor"),
        model_type=system_data.get("model_type"),
        model_source=system_data.get("model_source"),
        agentic_trace_required=system_data.get("agentic_trace_required")
    )
    db.add(new_system)
    db.commit()
    db.refresh(new_system)

    # Log action
    log_action(db, new_system.id, current_user, "SYSTEM_CREATED", {"name": new_system.name})

    return new_system

def get_systems(db: Session):
    """Retrieves all AI systems."""
    return db.query(AISystem).all()

def get_system_by_id(db: Session, system_id: str):
    """Retrieves a specific AI system."""
    return db.query(AISystem).filter(AISystem.id == system_id).first()

def update_status(db: Session, system_id: str, new_status: str, current_user: str, reason: str = ""):
    """Updates the compliance status of a system and logs the change."""
    system = db.query(AISystem).filter(AISystem.id == system_id).first()
    if system and system.compliance_status != new_status:
        old_status = system.compliance_status
        system.compliance_status = new_status
        db.commit()

        # Log action
        log_action(db, system_id, current_user, "STATUS_CHANGE", {
            "old_status": old_status,
            "new_status": new_status,
            "reason": reason
        })
    return system

def add_data_source(db: Session, system_id: str, source_data: dict, current_user: str):
    """Adds a data source to a system."""
    new_source = DataSource(
        system_id=system_id,
        source_name=source_data.get("source_name"),
        description=source_data.get("description"),
        contains_pii=source_data.get("contains_pii", 0),
        pii_categories=source_data.get("pii_categories", "")
    )
    db.add(new_source)
    db.commit()
    db.refresh(new_source)

    log_action(db, system_id, current_user, "DATA_SOURCE_ADDED", {"source_name": new_source.source_name})
    return new_source
