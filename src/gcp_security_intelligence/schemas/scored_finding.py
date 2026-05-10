from .enriched_finding import EnrichedFinding

class ScoredFinding(EnrichedFinding):
    """An EnrichedFinding with a risk score and reasoning from the risk analyst."""

    risk_score: str
    reasoning: str
