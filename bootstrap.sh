#!/bin/bash

sudo apt update && sudo apt upgrade -y

sudo apt install python3-venv python3-poetry -y

python3 -m venv .venv

source .venv/bin/activate

poetry install

read -sp "Enter Sudo Password: " ANSIBLE_SUDO_PASSWORD
echo ""

ansible-playbook -i inventory/local.yml playbooks/local-main.yml
