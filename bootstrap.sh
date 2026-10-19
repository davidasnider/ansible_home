#!/bin/bash
set -eo pipefail

echo "🚀 Starting system bootstrap..."

echo "🔄 [1/4] Updating package index and system packages..."
sudo apt update && sudo apt upgrade -y

echo "📦 [2/4] Installing curl and uv package manager..."
sudo apt install curl -y
curl -LsSf https://astral.sh/uv/install.sh | sh
if [ -f "$HOME/.cargo/env" ]; then
    source "$HOME/.cargo/env"
fi

echo "⚡ [3/4] Synchronizing Python dependencies..."
uv sync

echo "🛠️ [4/4] Executing Ansible site playbook..."
uv run ansible-playbook site.yml --ask-become-pass

echo "✨ System bootstrap completed successfully!"
