# Warden journal — ansible_home

## 2026-11-16 (branch hermes/warden-20261116-1712)
- code-13 (`actions/untrusted-checkout/high`) in `.github/workflows/claude-review.yml:31` is a real
  finding, not a false positive: the workflow (triggered by `issue_comment`, with only an
  `if:` guard on comment text/user) checks out the untrusted PR head ref and then runs
  `anthropics/claude-code-action`, which executes code in that same privileged context.
- Could not fix: the skill and harness forbid editing anything under `.github/`. Reported
  `not_fixed` with status `no_change`; the owner should fix it (e.g. drop or restrict
  permissions on this workflow, gate untrusted input before the checkout job, and run any
  execution step in a separate least-privileged job).
