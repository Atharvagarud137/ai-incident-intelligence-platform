from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.models.incident import IncidentSeverity, IncidentStatus
from app.schemas.incident import (
    IncidentCreate,
    IncidentUpdate,
    IncidentResponse,
    LogIngestRequest,
    LogIngestResponse,
)
from app.services.incident_service import (
    create_incident,
    get_incident,
    get_all_incidents,
    update_incident,
    delete_incident,
)
from app.core.logging import logger

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.post("/ingest", response_model=LogIngestResponse, status_code=status.HTTP_201_CREATED)
def ingest_logs(payload: LogIngestRequest, db: Session = Depends(get_db)):
    """
    Primary log ingestion endpoint.
    Accepts raw log content, creates an incident record, and prepares
    it for the chunking and embedding pipeline.
    """
    incident_data = IncidentCreate(
        title=payload.title,
        severity=payload.severity,
        raw_logs=payload.raw_logs,
    )
    incident = create_incident(db, incident_data)
    logger.info(f"Logs ingested | incident_id={incident.id} | log_size={len(payload.raw_logs)} chars")

    return LogIngestResponse(
        incident_id=incident.id,
        message="Logs ingested successfully. Ready for processing.",
        # Chunking pipeline will populate this — placeholder for now
        chunks_created=0,
    )


@router.get("/", response_model=list[IncidentResponse])
def list_incidents(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    status: Optional[IncidentStatus] = Query(default=None),
    severity: Optional[IncidentSeverity] = Query(default=None),
    db: Session = Depends(get_db),
):
    """List all incidents with optional filtering and pagination."""
    return get_all_incidents(db, skip=skip, limit=limit, status=status, severity=severity)


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident_by_id(incident_id: str, db: Session = Depends(get_db)):
    """Fetch a single incident by its ID."""
    incident = get_incident(db, incident_id)
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident {incident_id} not found.",
        )
    return incident


@router.patch("/{incident_id}", response_model=IncidentResponse)
def update_incident_by_id(
    incident_id: str, payload: IncidentUpdate, db: Session = Depends(get_db)
):
    """Partially update an incident — only provided fields are updated."""
    incident = update_incident(db, incident_id, payload)
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident {incident_id} not found.",
        )
    return incident


@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_incident_by_id(incident_id: str, db: Session = Depends(get_db)):
    """Delete an incident permanently."""
    deleted = delete_incident(db, incident_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident {incident_id} not found.",
        )