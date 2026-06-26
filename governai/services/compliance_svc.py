from sqlalchemy.orm import Session
from database.models import ComplianceRecord, AISystem

EU_AI_ACT_CONTROLS = {
    "High": [
        {"id": "EU-ART-14", "desc": "Human Oversight: Implement measures for human intervention."},
        {"id": "EU-ART-15", "desc": "Accuracy, Robustness, Cybersecurity: Ensure high levels of resilience."},
        {"id": "EU-ART-11", "desc": "Technical Documentation: Maintain up-to-date documentation."},
        {"id": "EU-ART-17", "desc": "Quality Management System: Establish a QMS for the AI lifecycle."}
    ],
    "Limited": [
        {"id": "EU-ART-52", "desc": "Transparency: Inform users they are interacting with an AI system."}
    ],
    "Minimal": [
        {"id": "EU-ART-69", "desc": "Code of Conduct: Voluntary adherence to trustworthy AI practices."}
    ]
}

def generate_checklists(db: Session, system_id: str):
    """Generates compliance records based on the system's risk tier."""
    system = db.query(AISystem).filter(AISystem.id == system_id).first()
    if not system or system.risk_tier == "Pending":
        return []
        
    tier = system.risk_tier
    if tier == "Prohibited":
        return []
        
    controls = EU_AI_ACT_CONTROLS.get(tier, [])
    
    # Check if already generated
    existing = db.query(ComplianceRecord).filter(ComplianceRecord.system_id == system_id).all()
    existing_ids = {r.control_id for r in existing}
    
    new_records = []
    for ctrl in controls:
        if ctrl["id"] not in existing_ids:
            record = ComplianceRecord(
                system_id=system_id,
                framework="EU AI Act",
                control_id=ctrl["id"],
                control_description=ctrl["desc"]
            )
            db.add(record)
            new_records.append(record)
            
    db.commit()
    return db.query(ComplianceRecord).filter(ComplianceRecord.system_id == system_id).all()

def update_compliance_record(db: Session, record_id: str, is_met: int, evidence_link: str):
    """Updates a single compliance control record."""
    record = db.query(ComplianceRecord).filter(ComplianceRecord.id == record_id).first()
    if record:
        record.is_met = is_met
        record.evidence_link = evidence_link
        db.commit()
    return record
    
def get_compliance_score(db: Session, system_id: str):
    """Calculates the percentage of met controls."""
    records = db.query(ComplianceRecord).filter(ComplianceRecord.system_id == system_id).all()
    if not records:
        return 0
    met_count = sum(1 for r in records if r.is_met)
    return int((met_count / len(records)) * 100)
