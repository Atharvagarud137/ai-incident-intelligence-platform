import uuid
from typing import Optional
from sqlalchemy.orm import Session
from app.models.incident import Incident, IncidentSeverity, IncidentStatus
from app.schemas.incident import IncidentCreate, IncidentUpdate
from app.core.logging import logger


def create_incident(db: Session, data: IncidentCreate) -> Incident:
    """
    Create a new incident record in the database.
    Generates a UUID for the incident ID.
    """
    incident = Incident(
        id=str(uuid.uuid4()),
        title=data.title,
        description=data.description,
        severity=data.severity,
        status=IncidentStatus.OPEN,
        raw_logs=data.raw_logs,
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    logger.info(f"Incident created | id={incident.id} | severity={incident.severity}")
    return incident


def get_incident(db: Session, incident_id: str) -> Optional[Incident]:
    """Fetch a single incident by ID. Returns None if not found."""
    return db.query(Incident).filter(Incident.id == incident_id).first()


def get_all_incidents(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    status: Optional[IncidentStatus] = None,
    severity: Optional[IncidentSeverity] = None,
) -> list[Incident]:
    """
    Fetch incidents with optional filtering by status and severity.
    Supports pagination via skip/limit.
    """
    query = db.query(Incident)

    if status:
        query = query.filter(Incident.status == status)
    if severity:
        query = query.filter(Incident.severity == severity)

    return query.order_by(Incident.created_at.desc()).offset(skip).limit(limit).all()


def update_incident(
    db: Session, incident_id: str, data: IncidentUpdate
) -> Optional[Incident]:
    """Update an existing incident with the provided fields."""
    incident = get_incident(db, incident_id)
    if not incident:
        return None

    # Only update fields that were explicitly provided
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(incident, field, value)

    db.commit()
    db.refresh(incident)
    logger.info(f"Incident updated | id={incident.id}")
    return incident


def delete_incident(db: Session, incident_id: str) -> bool:
    """Delete an incident. Returns True if deleted, False if not found."""
    incident = get_incident(db, incident_id)
    if not incident:
        return False

    db.delete(incident)
    db.commit()
    logger.info(f"Incident deleted | id={incident_id}")
    return True