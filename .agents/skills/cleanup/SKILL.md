---
name: cleanup
description: Safely cleans up the local repository after a PR is merged. Switches to main, pulls latest, prunes remotes, deletes the merged branch, and syncs dependencies.
---

1. Ensures a clean git state and a merged PR before cleaning up the local feature branch and syncing `main`.

// turbo
```bash
set -euo pipefail

CURRENT_BRANCH=$(git branch --show-current)

# 1. Safety Check: Don't run on main
if [ "$CURRENT_BRANCH" = "main" ]; then
    echo "ℹ️ Already on main branch. Nothing to clean up."
    exit 0
fi

# 2. Safety Check: Ensure git tree is clean
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ Error: Git tree is not clean. Please commit or stash your changes before cleaning up."
    exit 1
fi

# 3. Verify PR Status via GitHub CLI
echo "🔍 Checking PR status for branch: $CURRENT_BRANCH..."
PR_STATE=$(gh pr view --json state --jq .state 2>/dev/null || echo "UNKNOWN")

if [ "$PR_STATE" != "MERGED" ]; then
    echo "⚠️ Warning: PR for '$CURRENT_BRANCH' is not merged yet (State: $PR_STATE)."
    echo "Aborting cleanup to prevent data loss."
    exit 1
fi

# 4. Perform Cleanup
echo "🚀 PR is merged. Starting cleanup..."

echo "➡️ Switching to main..."
git checkout main

# Verify we successfully switched to main before pulling
if [ "$(git branch --show-current)" != "main" ]; then
    echo "❌ Error: Failed to switch to main branch."
    exit 1
fi

echo "📥 Pulling latest changes and pruning remotes..."
git pull --prune origin main

# 5. Safety Check: Verify no unique commits on the feature branch
echo "🔍 Verifying '$CURRENT_BRANCH' has no commits unique to main/origin-main..."
if git show-ref --verify --quiet refs/remotes/origin/main; then
    UNIQUE_COMMITS=$(git rev-list --count "origin/main..$CURRENT_BRANCH")
    BASE_REF="origin/main"
else
    # Fallback to local main if origin/main isn't available
    UNIQUE_COMMITS=$(git rev-list --count "main..$CURRENT_BRANCH")
    BASE_REF="main"
fi

if [ "$UNIQUE_COMMITS" -ne 0 ]; then
    echo "❌ Error: Branch '$CURRENT_BRANCH' still has $UNIQUE_COMMITS commit(s) not in $BASE_REF."
    echo "Aborting cleanup to avoid deleting unmerged or unpushed work."
    git log --oneline "$BASE_REF..$CURRENT_BRANCH"
    exit 1
fi

echo "🗑 Deleting local branch: $CURRENT_BRANCH..."
git branch -d -- "$CURRENT_BRANCH"

echo "🔄 Syncing dependencies..."
if command -v uv >/dev/null 2>&1; then
    uv sync
elif command -v poetry >/dev/null 2>&1; then
    poetry install
else
    echo "⚠️ Neither 'uv' nor 'poetry' found, skipping sync."
fi

echo "✅ Successfully cleaned up repository and synced main."
```
