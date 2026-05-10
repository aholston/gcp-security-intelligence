from pydantic import BaseModel
from .enriched_finding import EnrichedFinding


class EnrichedFindingList(BaseModel):
    """A list of enriched findings produced by the enrichment task."""

    findings: list[EnrichedFinding]
