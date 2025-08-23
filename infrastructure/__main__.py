"""
Infrastructure as Code for ansible_home repository management
"""

import pulumi
import pulumi_github as github

# Configuration
import os
github_token = os.getenv("GITHUB_TOKEN")
if not github_token:
    raise ValueError("GITHUB_TOKEN environment variable is required")

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
            "Auto Approve PR",
            "dependency-review",
            "pre-commit.ci - pr",
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

# Export repository information
pulumi.export("repository_name", repo.name)
pulumi.export("repository_url", repo.html_url)
pulumi.export("repository_clone_url", repo.git_clone_url)
