from .finding import Finding

class EnrichedFinding(Finding):
    """A Finding enriched with internal GCP context from audit logs and resource configuration."""

    log_activity: str 
    resource_configuration: str
    exploitation_evidence: str | None = None
