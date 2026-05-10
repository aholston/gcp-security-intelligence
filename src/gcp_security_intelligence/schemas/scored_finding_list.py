from pydantic import BaseModel
from .scored_finding import ScoredFinding


class ScoredFindingList(BaseModel):
    """A list of scored findings produced by the risk analysis task."""

    findings: list[ScoredFinding]
