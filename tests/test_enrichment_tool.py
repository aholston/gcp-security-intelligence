import json
import pytest
from unittest.mock import patch, MagicMock
from gcp_security_intelligence.tools.scanner_tool import SCCScannerTool
from gcp_security_intelligence.tools.enrichment_tool import EnrichmentTool


@pytest.fixture
def scanner_context():
    """Return raw scanner JSON string as enrichment tool input."""
    return SCCScannerTool()._run(project_id="test-project")


@pytest.fixture
def enriched_output(scanner_context):
    """Return parsed enrichment output with all GCP clients mocked."""
    with patch("gcp_security_intelligence.tools.enrichment_tool.compute_v1.FirewallsClient") as mock_fw, \
         patch("gcp_security_intelligence.tools.enrichment_tool.compute_v1.Firewall") as mock_fw_model, \
         patch("gcp_security_intelligence.tools.enrichment_tool.resourcemanager_v3.ProjectsClient") as mock_rm, \
         patch("gcp_security_intelligence.tools.enrichment_tool.storage.Client") as mock_storage:

        mock_fw.return_value.get.return_value = MagicMock()
        mock_fw_model.to_dict.return_value = {"name": "allow-all-ingress", "source_ranges": ["0.0.0.0/0"]}

        mock_policy = MagicMock()
        mock_binding = MagicMock()
        mock_binding.role = "roles/owner"
        mock_binding.members = ["serviceAccount:my-app-sa@test-project.iam.gserviceaccount.com"]
        mock_policy.bindings = [mock_binding]
        mock_rm.return_value.get_iam_policy.return_value = mock_policy

        mock_bucket = MagicMock()
        mock_bucket.get_iam_policy.return_value = {"roles/storage.objectViewer": ["allUsers"]}
        mock_storage.return_value.get_bucket.return_value = mock_bucket

        tool = EnrichmentTool()
        return json.loads(tool._run(context=scanner_context))


def test_all_findings_have_enrichment_key(enriched_output):
    """Every finding must have an enrichment key after processing."""
    for finding in enriched_output:
        assert "enrichment" in finding, f"Missing enrichment on: {finding['category']}"


def test_firewall_enrichment_contains_config(enriched_output):
    """Firewall finding enrichment must contain real firewall config fields."""
    firewall = next(f for f in enriched_output if f["category"] == "OPEN_FIREWALL")
    assert "name" in firewall["enrichment"]
    assert "source_ranges" in firewall["enrichment"]


def test_iam_enrichment_contains_bindings(enriched_output):
    """IAM finding enrichment must contain iam_bindings key."""
    iam = next(f for f in enriched_output if f["category"] == "ADMIN_SERVICE_ACCOUNT")
    assert "iam_bindings" in iam["enrichment"]


def test_storage_enrichment_contains_bindings(enriched_output):
    """Storage finding enrichment must contain iam_bindings key."""
    storage = next(f for f in enriched_output if f["category"] == "PUBLIC_BUCKET_ACL")
    assert "iam_bindings" in storage["enrichment"]


def test_mfa_enrichment_contains_note(enriched_output):
    """MFA finding enrichment must contain an org-level note."""
    mfa = next(f for f in enriched_output if f["category"] == "MFA_NOT_ENFORCED")
    assert "note" in mfa["enrichment"]


def test_original_fields_preserved(enriched_output):
    """Enrichment must not strip any fields from the original scanner output."""
    required = {"finding_name", "category", "severity", "affected_resource", "event_time", "description", "scc_context"}
    for finding in enriched_output:
        assert required.issubset(finding.keys())


def test_enrichment_error_handling(scanner_context):
    """A GCP client failure must produce an error key, not crash the pipeline."""
    with patch("gcp_security_intelligence.tools.enrichment_tool.compute_v1.FirewallsClient") as mock_fw, \
         patch("gcp_security_intelligence.tools.enrichment_tool.resourcemanager_v3.ProjectsClient") as mock_rm, \
         patch("gcp_security_intelligence.tools.enrichment_tool.storage.Client") as mock_storage:

        mock_fw.return_value.get.side_effect = Exception("GCP unavailable")
        mock_rm.return_value.get_iam_policy.side_effect = Exception("GCP unavailable")
        mock_storage.return_value.get_bucket.side_effect = Exception("GCP unavailable")

        tool = EnrichmentTool()
        result = json.loads(tool._run(context=scanner_context))

        for finding in result:
            if finding["category"] != "MFA_NOT_ENFORCED":
                assert "error" in finding["enrichment"]
