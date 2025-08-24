# README

## Cloning the Repository

To get started, clone this repository to your local machine:

```zsh
git clone https://github.com/davidasnider/ansible_home.git
cd ansible_home
```

On a Mac, you will first be prompted to install the Xcode command line tools. Follow the instructions to install them. Then run the above commands again.

## Installing

To set up your development environment, run:

```zsh
make dev-setup
```

This will:

- Remove any existing Poetry virtual environment
- Remove the `.env` file if it exists
- Create a new Python virtual environment in `.venv`
- Install all dependencies using Poetry

## Running the Local Setup Playbook

To automate your local environment setup, run the main Ansible playbook:

```zsh
source .venv/bin/activate
ansible-playbook -i inventory/local.yml playbooks/local-main.yml
```

This will automatically detect your OS (macOS or Linux) and apply the appropriate configuration tasks. Ensure you have Ansible installed and any required prerequisites met before running the playbook.

## GitHub MCP Setup

To enable GitHub integration with Claude Code, you'll need to set up the GitHub MCP server:

1. First, export your GitHub Personal Access Token:
   ```zsh
   export GITHUB_TOKEN=<your-PAT>
   ```

2. Add the GitHub MCP server to Claude:
   ```zsh
   claude mcp add github https://api.githubcopilot.com/mcp/ \
       --header "Authorization: Bearer $GITHUB_TOKEN" \
       --transport http
   ```

This will allow Claude Code to interact with GitHub repositories, issues, and pull requests.
