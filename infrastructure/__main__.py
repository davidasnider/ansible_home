"""
Infrastructure as Code for ansible_home repository management
"""

import pulumi
import pulumi_github as github
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Configuration
github_token = os.getenv("GITHUB_TOKEN")
if not github_token:
    raise ValueError("GITHUB_TOKEN environment variable is required")

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key or gemini_api_key == "YOUR_API_KEY":  # pragma: allowlist secret
    raise ValueError("GEMINI_API_KEY environment variable is required and must be set in the .env file")

# Import existing repository instead of creating new one
repo = github.Repository(
    "ansible-home",
    name="ansible_home",
    description="Ansible configuration for home automation and system setup",
    visibility="public",
    has_issues=True,
    has_projects=False,
    has_wiki=False,
    allow_merge_commit=True,
    allow_squash_merge=True,
    allow_rebase_merge=True,
    allow_auto_merge=True,
    delete_branch_on_merge=True,
    vulnerability_alerts=True,
    security_and_analysis=github.RepositorySecurityAndAnalysisArgs(
        secret_scanning=github.RepositorySecurityAndAnalysisSecretScanningArgs(
            status="enabled"
        ),
        secret_scanning_push_protection=github.RepositorySecurityAndAnalysisSecretScanningPushProtectionArgs(
            status="enabled"
        ),
    ),
    opts=pulumi.ResourceOptions(import_="ansible_home")
)

# Branch protection for main branch
branch_protection = github.BranchProtection(
    "main-protection",
    repository_id=repo.node_id,
    pattern="main",
    enforce_admins=True,
    required_status_checks=github.BranchProtectionRequiredStatusCheckArgs(
        strict=True,
        contexts=[
            # CI & Quality Checks workflow
            "Ansible Linting",
            "Pre-commit Checks",
            "Secret Scanning",
            "Ansible Syntax Check",
            "Dependency Review",
            "Wait for Molecule Tests",
            # Molecule Testing workflow - comprehensive final status check
            "All Molecule Tests",
        ],
    ),
    required_pull_request_reviews=github.BranchProtectionRequiredPullRequestReviewArgs(
        required_approving_review_count=1,
        dismiss_stale_reviews=True,
        require_code_owner_reviews=False,
        restrict_dismissals=False,
    ),
    allows_force_pushes=False,
    allows_deletions=False,
    require_signed_commits=True,
    require_conversation_resolution=True,
    required_linear_history=True,
)

# GitHub Actions Secret for Gemini API Key
gemini_secret = github.ActionsSecret("gemini-api-key-secret",
    repository=repo.name,
    secret_name="GEMINI_API_KEY",
    plaintext_value=gemini_api_key,  # pragma: allowlist secret
)

# Export repository information
pulumi.export("repository_name", repo.name)
pulumi.export("repository_url", repo.html_url)
pulumi.export("repository_clone_url", repo.git_clone_url)
pulumi.export("gemini_secret_name", gemini_secret.secret_name)

# Export branch protection information
pulumi.export("branch_protection_enabled", True)
pulumi.export("required_status_checks", [
    "Ansible Linting",
    "Pre-commit Checks",
    "Secret Scanning",
    "Ansible Syntax Check",
    "Dependency Review",
    "Wait for Molecule Tests",
    "All Molecule Tests"
])
pulumi.export("required_reviews", 1)
pulumi.export("require_conversation_resolution", True)
