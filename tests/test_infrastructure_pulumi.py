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
            # Normalize securityAndAnalysis/security_and_analysis to a list containing the dict
            sec_analysis = outputs.pop("securityAndAnalysis", None) or outputs.get("security_and_analysis")
            if sec_analysis and isinstance(sec_analysis, dict):
                outputs["security_and_analysis"] = [sec_analysis]

        elif args.typ == "github:index/branchProtection:BranchProtection":
            # Normalize requiredStatusChecks/required_status_checks to a list containing the dict
            status_checks = outputs.pop("requiredStatusChecks", None) or outputs.get("required_status_checks")
            if status_checks and isinstance(status_checks, dict):
                outputs["required_status_checks"] = [status_checks]

            # Normalize requiredPullRequestReviews/required_pull_request_reviews to a list containing the dict
            pr_reviews = outputs.pop("requiredPullRequestReviews", None) or outputs.get("required_pull_request_reviews")
            if pr_reviews and isinstance(pr_reviews, dict):
                outputs["required_pull_request_reviews"] = [pr_reviews]

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
        pattern, enforce_admins, req_reviews, linear_history, req_status_checks = args
        assert pattern == "main"
        assert enforce_admins is True

        if isinstance(req_reviews, list) and len(req_reviews) > 0:
            rr = req_reviews[0]
            count = rr.get("required_approving_review_count") or rr.get("requiredApprovingReviewCount")
            assert count == 1

        assert linear_history is True

        if isinstance(req_status_checks, list) and len(req_status_checks) > 0:
            sc = req_status_checks[0]
            assert sc.get("strict") is True
            contexts = sc.get("contexts")
            expected_contexts = [
                "Ansible Linting",
                "Pre-commit Checks",
                "Secret Scanning",
                "Ansible Syntax Check",
                "Dependency Review",
            ]
            assert contexts == expected_contexts

    return pulumi.Output.all(
        infra.branch_protection.pattern,
        infra.branch_protection.enforce_admins,
        infra.branch_protection.required_pull_request_reviews,
        infra.branch_protection.required_linear_history,
        infra.branch_protection.required_status_checks
    ).apply(check)
