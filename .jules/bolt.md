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

## 2024-05-18 - [Ansible: Native Shell Task Idempotency]
**Learning:** Checking for file existence with a separate `ansible.builtin.stat` task before running a shell command that creates it adds unnecessary overhead (connection setup, module execution, task parsing) and violates the principle of letting Ansible handle idempotency natively.
**Action:** Remove redundant `ansible.builtin.stat` + `when` condition combinations and rely exclusively on the `creates` argument within `ansible.builtin.shell` or `ansible.builtin.command` to skip execution if the target file or directory already exists.

## 2026-09-09 - dpkg --print-architecture reports the userspace ABI, not the kernel arch
**Learning:** `dpkg --print-architecture` reports the Debian **userspace/ABI** (e.g. `amd64`, `i386`, `armhf`, `arm64`), while `ansible_facts['architecture']` reports the **kernel/machine** architecture from `uname -m` (e.g. `x86_64`, `i686`, `armv7l`, `aarch64`). On mixed-ABI hosts — e.g. a Raspberry Pi with a 64-bit kernel and 32-bit Debian userland — they diverge: the fact is `aarch64` while dpkg reports `armhf`. There is no built-in Ansible fact that exposes the Debian userspace ABI, so mapping `ansible_facts['architecture']` for APT repository arch selectors/URLs can select the wrong architecture (e.g. `arm64` instead of `armhf`) and make the repository unavailable.
**Action:** Keep a `dpkg --print-architecture` task (with `changed_when: false`) as the source of truth for Debian architecture selectors in APT repository lines; do not substitute `ansible_facts['architecture']`.
## 2024-05-24 - Ansible Copy native force False over Stat
**Learning:** Checking for file existence with `ansible.builtin.stat` and conditionally running a subsequent task introduces unneeded overhead (parsing and connections). Using `ansible.builtin.copy` with `force: false` skips overwriting the file if it exists, fulfilling the exact same idempotency requirement in a single task.
**Action:** When conditionally writing a file based on existence, use `ansible.builtin.copy` with `force: false` instead of a paired `stat` and conditional block.
