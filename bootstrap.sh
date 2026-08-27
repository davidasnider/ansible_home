#!/bin/bash

sudo apt update && sudo apt upgrade -y

sudo apt install curl -y
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env

uv sync

uv run ansible-playbook site.yml --ask-become-pass
