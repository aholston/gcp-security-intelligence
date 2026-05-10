from pydantic import BaseModel

class SecurityReport(BaseModel):
    """Final report containing an executive summary and a technical remediation runbook."""

    executive_summary: str
    technical_runbook: str