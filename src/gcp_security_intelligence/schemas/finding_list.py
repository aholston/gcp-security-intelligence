from pydantic import BaseModel
from .finding import Finding


class FindingList(BaseModel):
    """A list of SCC findings produced by the scanner task."""

    findings: list[Finding]
