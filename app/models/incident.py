import uuid
from sqlalchemy import String, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin
import enum


class IncidentSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(str, enum.Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Incident(Base, TimestampMixin):
    """
    Core incident model — represents a single operational incident.
    Logs, RCA, and embeddings all link back to this.
    """
    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    severity: Mapped[IncidentSeverity] = mapped_column(
        SAEnum(IncidentSeverity), nullable=False, default=IncidentSeverity.MEDIUM
    )
    status: Mapped[IncidentStatus] = mapped_column(
        SAEnum(IncidentStatus), nullable=False, default=IncidentStatus.OPEN
    )
    # AI-generated root cause analysis stored here after processing
    rca_summary: Mapped[str] = mapped_column(Text, nullable=True)
    # Raw log content associated with this incident
    raw_logs: Mapped[str] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Incident id={self.id} title={self.title} severity={self.severity}>"