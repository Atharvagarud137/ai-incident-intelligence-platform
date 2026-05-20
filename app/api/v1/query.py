from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional

from app.core.database import get_db
from app.services.rag_service import query_incident, generate_rca
from app.services.incident_service import get_incident, update_incident
from app.schemas.incident import IncidentUpdate
from app.core.logging import logger

router = APIRouter(prefix="/query", tags=["RAG Query"])


class QueryRequest(BaseModel):
    """Request schema for RAG-based incident querying."""
    query: str = Field(..., min_length=5, description="Question about the incident or logs.")
    incident_id: Optional[str] = Field(
        None, description="Scope query to a specific incident. Leave empty to search all."
    )
    top_k: int = Field(default=5, ge=1, le=20, description="Number of log chunks to retrieve.")


class QueryResponse(BaseModel):
    """Response schema for RAG queries."""
    query: str
    response: str
    chunks_used: int
    sources: list


class RCAResponse(BaseModel):
    """Response schema for RCA generation."""
    incident_id: str
    rca: str
    chunks_analyzed: int


@router.post("/ask", response_model=QueryResponse)
async def ask_question(payload: QueryRequest):
    """
    RAG-powered Q&A endpoint.
    Ask any question about ingested incidents and logs.
    The platform retrieves relevant log chunks and generates
    a grounded AI response.
    """
    try:
        result = await query_incident(
            query=payload.query,
            incident_id=payload.incident_id,
            top_k=payload.top_k,
        )
        return QueryResponse(
            query=payload.query,
            response=result["response"],
            chunks_used=result["chunks_used"],
            sources=result["sources"],
        )
    except Exception as e:
        logger.error(f"RAG query failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Query processing failed. Please try again.",
        )


@router.post("/rca/{incident_id}", response_model=RCAResponse)
async def generate_incident_rca(incident_id: str, db: Session = Depends(get_db)):
    """
    Generate an AI-powered Root Cause Analysis for a specific incident.
    Analyzes all ingested log chunks for the incident and produces
    a structured RCA report covering timeline, root cause, and recommendations.
    """
    # Verify the incident exists before running RCA
    incident = get_incident(db, incident_id)
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident {incident_id} not found.",
        )

    try:
        result = await generate_rca(incident_id)

        # Persist the RCA summary back to the incident record
        update_incident(
            db,
            incident_id,
            IncidentUpdate(rca_summary=result["rca"]),
        )

        return RCAResponse(
            incident_id=incident_id,
            rca=result["rca"],
            chunks_analyzed=result["chunks_analyzed"],
        )
    except Exception as e:
        logger.error(f"RCA generation failed | incident_id={incident_id} | error={e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="RCA generation failed. Please try again.",
        )