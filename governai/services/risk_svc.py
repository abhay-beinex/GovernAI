from sqlalchemy.orm import Session
from database.models import RiskAssessment, RiskClassificationAnswer, AISystem
from services.audit_svc import log_action

# Simplified EU AI Act Questionnaire
RISK_QUESTIONS = [
    {
        "key": "q1_biometric",
        "text": "Does this system perform real-time remote biometric identification in publicly accessible spaces?",
        "options": ["Yes", "No"],
        "high_risk_trigger": "Yes"
    },
    {
        "key": "q2_critical_infra",
        "text": "Is this system intended to be used as a safety component in the management of critical infrastructure?",
        "options": ["Yes", "No"],
        "high_risk_trigger": "Yes"
    },
    {
        "key": "q3_employment",
        "text": "Is this system used for recruitment, task allocation, or performance evaluation in an employment context?",
        "options": ["Yes", "No"],
        "high_risk_trigger": "Yes"
    }
]

def assess_risk(db: Session, system_id: str, answers: dict, current_user: str):
    """Evaluates risk questionnaire answers and assigns a tier."""
    
    # 1. Determine Tier
    assigned_tier = "Minimal"
    for q in RISK_QUESTIONS:
        if answers.get(q["key"]) == q["high_risk_trigger"]:
            assigned_tier = "High"
            break
            
    # Additional logic: Check for PII in data sources (auto-raise risk)
    system = db.query(AISystem).filter(AISystem.id == system_id).first()
    if assigned_tier != "High":
        for ds in system.data_sources:
            if ds.contains_pii:
                assigned_tier = "Limited" # Raise to at least limited if it has PII
                break
                
    # 2. Save Assessment
    assessment = RiskAssessment(
        system_id=system_id,
        calculated_tier=assigned_tier,
        assessed_by=current_user
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    
    # 3. Save Answers
    for key, val in answers.items():
        ans_record = RiskClassificationAnswer(
            assessment_id=assessment.id,
            question_key=key,
            answer=val
        )
        db.add(ans_record)
        
    # 4. Update System Tier
    system.risk_tier = assigned_tier
    db.commit()
    
    # 5. Log Action
    log_action(db, system_id, current_user, "TIER_ASSIGNED", {"assigned_tier": assigned_tier})
    
    return assessment
