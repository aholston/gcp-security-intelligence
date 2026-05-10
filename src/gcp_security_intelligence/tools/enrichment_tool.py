from crewai.tools import BaseTool
import json
from google.cloud import compute_v1
from google.cloud import resourcemanager_v3
from google.cloud import storage


class EnrichmentTool(BaseTool):
    name: str = "Enrichment Tool"
    description: str = "Takes SCC findings as JSON and enriches each one with relevant GCP context based on finding type."

    def _run(self, context: str) -> str:
        """Enrich each finding with GCP resource context based on its category."""
        findings = json.loads(context)
        enriched = []
        for finding in findings:
            category = finding["category"]
            project_id = finding["finding_name"].split("/")[1]

            try:
                if category == "OPEN_FIREWALL":
                    client = compute_v1.FirewallsClient()
                    firewall_name = finding["affected_resource"].split("/")[-1]
                    result = client.get(project=project_id, firewall=firewall_name)
                    finding["enrichment"] = compute_v1.Firewall.to_dict(result)

                elif category == "ADMIN_SERVICE_ACCOUNT":
                    client = resourcemanager_v3.ProjectsClient()
                    policy = client.get_iam_policy(request={"resource": f"projects/{project_id}"})
                    sa_email = finding["affected_resource"].split("/")[-1]
                    sa_bindings = [
                        {"role": b.role, "members": list(b.members)}
                        for b in policy.bindings
                        if any(sa_email in m for m in b.members)
                    ]
                    finding["enrichment"] = {"iam_bindings": sa_bindings}

                elif category == "PUBLIC_BUCKET_ACL":
                    client = storage.Client(project=project_id)
                    bucket_name = finding["affected_resource"].split("/")[-1]
                    bucket = client.get_bucket(bucket_name)
                    policy = bucket.get_iam_policy()
                    finding["enrichment"] = {
                        "iam_bindings": {role: list(members) for role, members in policy.items()}
                    }

                elif category == "MFA_NOT_ENFORCED":
                    # MFA enforcement is an org-level policy — not queryable at project scope
                    finding["enrichment"] = {
                        "note": "MFA enforcement status requires org-level access to query. Manual verification required."
                    }

            except Exception as e:
                finding["enrichment"] = {"error": str(e)}

            enriched.append(finding)

        return json.dumps(enriched, default=str)


if __name__ == "__main__":
    from scanner_tool import SCCScannerTool
    scanner_output = SCCScannerTool()._run(project_id="scc-security-intelligence")
    tool = EnrichmentTool()
    print(tool._run(context=scanner_output))
