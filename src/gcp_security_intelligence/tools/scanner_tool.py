from crewai.tools import BaseTool
from datetime import datetime, UTC, timedelta
import json

class SCCScannerTool(BaseTool):
    name: str = "SCC Scanner Tool"
    description: str = "Returns active SCC findings from the last 24 hours for a given GCP project."

    def _run(self, project_id: str) -> str:
        """Return mock SCC findings shaped like real SCC API responses."""
        event_time = (datetime.now(UTC) - timedelta(hours=4)).isoformat()

        findings = [
            {
                "finding_name": f"projects/{project_id}/sources/1234/findings/aaa111",
                "category": "OPEN_FIREWALL",
                "severity": "HIGH",
                "affected_resource": f"//compute.googleapis.com/projects/{project_id}/global/firewalls/allow-all-ingress",
                "event_time": event_time,
                "description": "Firewall rule allows ingress traffic from 0.0.0.0/0 on all ports.",
                "scc_context": {
                    "mitre_attack": {"tactic": "Initial Access", "technique": "T1190"},
                    "cvss_score": None
                }
            },
            {
                "finding_name": f"projects/{project_id}/sources/1234/findings/bbb222",
                "category": "ADMIN_SERVICE_ACCOUNT",
                "severity": "CRITICAL",
                "affected_resource": f"//iam.googleapis.com/projects/{project_id}/serviceAccounts/my-app-sa@{project_id}.iam.gserviceaccount.com",
                "event_time": event_time,
                "description": "Service account has been granted the Owner role at the project level.",
                "scc_context": {
                    "mitre_attack": {"tactic": "Privilege Escalation", "technique": "T1078"},
                    "cvss_score": None
                }
            },
            {
                "finding_name": f"projects/{project_id}/sources/1234/findings/ccc333",
                "category": "PUBLIC_BUCKET_ACL",
                "severity": "MEDIUM",
                "affected_resource": f"//storage.googleapis.com/projects/{project_id}/buckets/my-app-data-bucket",
                "event_time": event_time,
                "description": "Cloud Storage bucket is publicly accessible via allUsers ACL.",
                "scc_context": {
                    "mitre_attack": {"tactic": "Exfiltration", "technique": "T1530"},
                    "cvss_score": None
                }
            },
            {
                "finding_name": f"projects/{project_id}/sources/1234/findings/ddd444",
                "category": "MFA_NOT_ENFORCED",
                "severity": "MEDIUM",
                "affected_resource": f"//cloudresourcemanager.googleapis.com/projects/{project_id}",
                "event_time": event_time,
                "description": "Multi-factor authentication is not enforced for users with project access.",
                "scc_context": {
                    "mitre_attack": {"tactic": "Credential Access", "technique": "T1556"},
                    "cvss_score": None
                }
            }
        ]

        return json.dumps(findings, indent=2)

if __name__ == "__main__":
    tool = SCCScannerTool()
    result = tool._run(project_id="scc-security-intelligence")
    print(result)