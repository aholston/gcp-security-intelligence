from pydantic import BaseModel
from datetime import datetime

class Finding(BaseModel):
    """A single SCC finding from the scanner task."""

    finding_name: str
    category: str
    severity: str
    affected_resource: str
    event_time: datetime
    description: str
    scc_context: dict