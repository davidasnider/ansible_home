## 2024-05-24 - Ansible Execution Overhead
**Learning:** Consolidating multiple similar Ansible module calls (like `community.general.git_config`) into a single task with a `loop` reduces task execution overhead (setup, plugin loading, and connection management).
**Action:** Always look for sequential calls to the same module and group them using `loop`.

## 2026-08-23 - Consolidate apt update and install
**Learning:** In Ansible, `ansible.builtin.apt` can update the cache (`update_cache: true`) and install a package (`name`) in a single task, eliminating the overhead of running two separate tasks and establishing two separate connections. Note that combining `update_cache: true` with a package install does not require `cache_valid_time` if the cache was just updated with a new repository via `apt_repository`.
**Action:** Always combine `update_cache` and package installation in a single `apt` module task when updating the cache right before an install.

## 2026-08-23 - Prevent Redundant APT Cache Updates After Adding Repos
**Learning:** Adding a repository and then subsequently running an `apt` module task with `update_cache: true` works, but causes unconditional cache updates on every playbook run if `cache_valid_time` isn't used. However, applying `cache_valid_time` right after adding a repository without updating the cache *first* can cause the new package not to be found. The correct pattern is to add `update_cache: true` directly to the `ansible.builtin.apt_repository` task so the cache is updated immediately *only* when the repo is first added or changed. Then, the subsequent `ansible.builtin.apt` task can safely use both `update_cache: true` and `cache_valid_time: 86400` to prevent redundant updates on future runs.
**Action:** When adding a repository and installing its packages, use `update_cache: true` in `apt_repository`, and then use both `update_cache: true` and `cache_valid_time: 86400` in the subsequent `apt` installation task.

## 2024-05-24 - Consolidate Ansible command loops into multiline shell blocks
**Learning:** Looping over `ansible.builtin.command` causes per-iteration task parsing and setup overhead.
**Action:** To optimize Ansible loops over command/shell tasks, consolidate the iterations into a single multiline `ansible.builtin.shell` block.
