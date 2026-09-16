## 2024-05-24 - Ansible Execution Overhead
**Learning:** Consolidating multiple similar Ansible module calls (like `community.general.git_config`) into a single task with a `loop` reduces task execution overhead (setup, plugin loading, and connection management).
**Action:** Always look for sequential calls to the same module and group them using `loop`.

## 2026-08-23 - Consolidate apt update and install
**Learning:** In Ansible, `ansible.builtin.apt` can update the cache (`update_cache: true`) and install a package (`name`) in a single task, eliminating the overhead of running two separate tasks and establishing two separate connections. Note that combining `update_cache: true` with a package install does not require `cache_valid_time` if the cache was just updated with a new repository via `apt_repository`.
**Action:** Always combine `update_cache` and package installation in a single `apt` module task when updating the cache right before an install.

## 2026-08-23 - Prevent Redundant APT Cache Updates After Adding Repos
**Learning:** Adding a repository and then subsequently running an `apt` module task with `update_cache: true` works, but causes unconditional cache updates on every playbook run if `cache_valid_time` isn't used. However, applying `cache_valid_time` right after adding a repository without updating the cache *first* can cause the new package not to be found. The correct pattern is to add `update_cache: true` directly to the `ansible.builtin.apt_repository` task so the cache is updated immediately *only* when the repo is first added or changed. Then, the subsequent `ansible.builtin.apt` task can safely use both `update_cache: true` and `cache_valid_time: 86400` to prevent redundant updates on future runs.
**Action:** When adding a repository and installing its packages, use `update_cache: true` in `apt_repository`, and then use both `update_cache: true` and `cache_valid_time: 86400` in the subsequent `apt` installation task.

## 2026-09-05 - Ansible performance shell script commands
**Learning:** For some Ansible shell command task loops, executing a single `ansible.builtin.shell` command that runs multiple successive scripts in a YAML `|` (literal block scalar) multiline block eliminates the Ansible loop task startup, parse, and setup overhead for each iteration. Using a shell `for` loop inside that block keeps the shell usage clearly required (satisfying the `command-instead-of-shell` lint rule) while keeping the item list easy to extend.
**Action:** When a loop involves running a sequence of identical fast scripts with varying arguments, consider moving the loop into a single `shell` command using a YAML `|` (literal block scalar) block — with a shell `for` loop when iterating over items — instead of a task `loop`.

## 2024-11-20 - Ansible User Facts
**Learning:** Shell commands like `whoami` have an implicit task execution overhead. The built-in `ansible_facts['user_id']` contains the current running user ID and can be used in its place to skip running a separate command.
**Action:** Use `ansible_facts['user_id']` instead of creating new tasks that run `whoami`.
## 2024-05-24 - Ansible Native Facts vs Shelling Out
**Learning:** Shelling out to run commands like `dpkg --print-architecture` introduces significant overhead due to task setup, connection overhead, and executing a separate process. Ansible facts are already populated during the fact gathering phase. Using mapped native facts via a Jinja expression (e.g., `ansible_facts['architecture']`) is much more efficient than using a `ansible.builtin.command` task just to set a variable.
**Action:** Replace `ansible.builtin.command: dpkg --print-architecture` tasks with Jinja2 `ansible_facts['architecture']` mappings directly in the templates/tasks.
