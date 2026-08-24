## 2024-05-24 - Ansible Execution Overhead
**Learning:** Consolidating multiple similar Ansible module calls (like `community.general.git_config`) into a single task with a `loop` reduces task execution overhead (setup, plugin loading, and connection management).
**Action:** Always look for sequential calls to the same module and group them using `loop`.

## 2026-08-23 - Consolidate apt update and install
**Learning:** In Ansible, `ansible.builtin.apt` can update the cache (`update_cache: true`) and install a package (`name`) in a single task, eliminating the overhead of running two separate tasks and establishing two separate connections. Note that combining `update_cache: true` with a package install does not require `cache_valid_time` if the cache was just updated with a new repository via `apt_repository`.
**Action:** Always combine `update_cache` and package installation in a single `apt` module task when updating the cache right before an install.
