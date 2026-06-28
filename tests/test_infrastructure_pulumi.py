import os
import sys
import pytest
import pulumi
from pathlib import Path

# Add the root directory to PYTHONPATH so infrastructure module can be found
sys.path.append(str(Path(__file__).parent.parent))

class PulumiMocks(pulumi.runtime.Mocks):
    def new_resource(self, args: pulumi.runtime.MockResourceArgs):
        outputs = dict(args.inputs)
        if args.typ == "github:index/repository:Repository":
            outputs = {
                **outputs,
                "name": outputs.get("name", "ansible_home"),
                "html_url": "https://github.com/test/ansible_home",
                "git_clone_url": "https://github.com/test/ansible_home.git",
                "node_id": "test_node_id"
            }
            if "securityAndAnalysis" in outputs and isinstance(outputs["securityAndAnalysis"], dict):
                outputs["security_and_analysis"] = [outputs.pop("securityAndAnalysis")]
            elif "security_and_analysis" in outputs and isinstance(outputs["security_and_analysis"], dict):
                outputs["security_and_analysis"] = [outputs["security_and_analysis"]]

        elif args.typ == "github:index/branchProtection:BranchProtection":
            for list_prop in ["requiredStatusChecks", "requiredPullRequestReviews", "required_status_checks", "required_pull_request_reviews"]:
                if list_prop in outputs and isinstance(outputs[list_prop], dict):
                    prop_name = "required_status_checks" if "StatusChecks" in list_prop or "status_checks" in list_prop else "required_pull_request_reviews"
                    outputs[prop_name] = [outputs.pop(list_prop) if list_prop != prop_name else outputs[list_prop]]

        return [args.name + '_id', outputs]

    def call(self, args: pulumi.runtime.MockCallArgs):
        return {}

@pytest.fixture(scope="module")
def infra():
    old_env = os.environ.get("GITHUB_TOKEN")
    os.environ["GITHUB_TOKEN"] = "dummy_token"

    pulumi.runtime.set_mocks(PulumiMocks())
    import infrastructure.__main__ as infra_module

    yield infra_module

    if old_env is not None:
        os.environ["GITHUB_TOKEN"] = old_env
    else:
        del os.environ["GITHUB_TOKEN"]

@pytest.mark.unit
@pulumi.runtime.test
def test_repository_configuration(infra):
    """Test repository resource properties."""
    def check(args):
        name, visibility, has_issues, security_analysis = args
        assert name == "ansible_home"
        assert visibility == "public"
        assert has_issues is True
        # Extract secret scanning status
        # Pulumi might convert camelCase to snake_case or vice versa
        if isinstance(security_analysis, list) and len(security_analysis) > 0:
            sa = security_analysis[0]
            if "secret_scanning" in sa:
                assert sa["secret_scanning"]["status"] == "enabled"
            elif "secretScanning" in sa:
                assert sa["secretScanning"]["status"] == "enabled"

    return pulumi.Output.all(
        infra.repo.name,
        infra.repo.visibility,
        infra.repo.has_issues,
        infra.repo.security_and_analysis
    ).apply(check)

@pytest.mark.unit
@pulumi.runtime.test
def test_branch_protection_configuration(infra):
    """Test branch protection resource properties."""
    def check(args):
        pattern, enforce_admins, req_reviews, linear_history = args
        assert pattern == "main"
        assert enforce_admins is True

        if isinstance(req_reviews, list) and len(req_reviews) > 0:
            rr = req_reviews[0]
            count = rr.get("required_approving_review_count") or rr.get("requiredApprovingReviewCount")
            assert count == 1

        assert linear_history is True

    return pulumi.Output.all(
        infra.branch_protection.pattern,
        infra.branch_protection.enforce_admins,
        infra.branch_protection.required_pull_request_reviews,
        infra.branch_protection.required_linear_history
    ).apply(check)
