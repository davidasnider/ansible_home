#!/bin/bash

sudo apt update && sudo apt upgrade -y

sudo apt install curl -y
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env

uv sync

read -sp "Enter Sudo Password: " ANSIBLE_SUDO_PASSWORD
echo ""
export ANSIBLE_SUDO_PASS="$ANSIBLE_SUDO_PASSWORD"

uv run ansible-playbook playbooks/workstations.yml
