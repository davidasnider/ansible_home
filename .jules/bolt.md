## 2024-05-24 - Ansible Execution Overhead
**Learning:** Consolidating multiple similar Ansible module calls (like `community.general.git_config`) into a single task with a `loop` reduces task execution overhead (setup, plugin loading, and connection management).
**Action:** Always look for sequential calls to the same module and group them using `loop`.
