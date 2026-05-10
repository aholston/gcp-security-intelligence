import json
import pytest
from gcp_security_intelligence.tools.scanner_tool import SCCScannerTool

REQUIRED_FIELDS = {"finding_name", "category", "severity", "affected_resource", "event_time", "description", "scc_context"}


@pytest.fixture
def scanner_output():
    """Return parsed scanner output for a test project."""
    tool = SCCScannerTool()
    return json.loads(tool._run(project_id="test-project"))


def test_returns_valid_json():
    """Scanner output must be a valid JSON array."""
    tool = SCCScannerTool()
    result = tool._run(project_id="test-project")
    parsed = json.loads(result)
    assert isinstance(parsed, list)


def test_returns_four_findings(scanner_output):
    """Scanner must return exactly four mock findings."""
    assert len(scanner_output) == 4


def test_all_findings_have_required_fields(scanner_output):
    """Every finding must contain all required fields."""
    for finding in scanner_output:
        assert REQUIRED_FIELDS.issubset(finding.keys()), f"Missing fields in: {finding}"


def test_finding_names_scoped_to_project(scanner_output):
    """Finding names must reference the requested project ID."""
    for finding in scanner_output:
        assert "test-project" in finding["finding_name"]


def test_severity_values_are_valid(scanner_output):
    """All severity values must be one of the four valid SCC tiers."""
    valid = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
    for finding in scanner_output:
        assert finding["severity"] in valid


def test_scc_context_contains_mitre(scanner_output):
    """Every finding must include MITRE ATT&CK context."""
    for finding in scanner_output:
        assert "mitre_attack" in finding["scc_context"]
        assert "tactic" in finding["scc_context"]["mitre_attack"]
        assert "technique" in finding["scc_context"]["mitre_attack"]


def test_expected_categories_present(scanner_output):
    """All four expected finding categories must be present."""
    categories = {f["category"] for f in scanner_output}
    assert categories == {"OPEN_FIREWALL", "ADMIN_SERVICE_ACCOUNT", "PUBLIC_BUCKET_ACL", "MFA_NOT_ENFORCED"}
