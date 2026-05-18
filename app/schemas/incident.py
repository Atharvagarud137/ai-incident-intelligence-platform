from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.incident import IncidentSeverity, IncidentStatus


class IncidentCreate(BaseModel):
    """Schema for creating a new incident."""
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = Field(None)
    severity: IncidentSeverity = Field(default=IncidentSeverity.MEDIUM)
    raw_logs: Optional[str] = Field(None)


class IncidentUpdate(BaseModel):
    """Schema for updating an existing incident."""
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None)
    severity: Optional[IncidentSeverity] = Field(None)
    status: Optional[IncidentStatus] = Field(None)
    rca_summary: Optional[str] = Field(None)
    raw_logs: Optional[str] = Field(None)


class IncidentResponse(BaseModel):
    """Schema for returning incident data in API responses."""
    id: str
    title: str
    description: Optional[str]
    severity: IncidentSeverity
    status: IncidentStatus
    rca_summary: Optional[str]
    raw_logs: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LogIngestRequest(BaseModel):
    """
    Schema for the log ingestion endpoint.
    Accepts raw log text with optional metadata.
    """
    incident_id: Optional[str] = Field(
        None, description="Link logs to an existing incident, or leave empty to auto-create one."
    )
    title: str = Field(..., min_length=3, max_length=255)
    severity: IncidentSeverity = Field(default=IncidentSeverity.MEDIUM)
    raw_logs: str = Field(..., min_length=10, description="Raw log content to ingest.")


class LogIngestResponse(BaseModel):
    """Response returned after successful log ingestion."""
    incident_id: str
    message: str
    chunks_created: int