#!/bin/bash
set -eo pipefail

echo "🚀 Starting system bootstrap..."

if ! command -v apt >/dev/null 2>&1; then
    echo "❌ 'apt' package manager not found. bootstrap.sh is designed for Ubuntu/Debian systems." >&2
    echo "💡 For macOS, please run 'make dev-setup' instead." >&2
    exit 1
fi

echo "🔄 [1/4] Updating package index and system packages..."
sudo apt update && sudo apt upgrade -y

echo "📦 [2/4] Installing curl and uv package manager..."
sudo apt install curl -y
if command -v uv >/dev/null 2>&1; then
    echo "  ℹ️ uv is already installed ($(uv --version))"
else
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi
if [ -f "$HOME/.local/bin/env" ]; then
    source "$HOME/.local/bin/env"
elif [ -f "$HOME/.cargo/env" ]; then
    source "$HOME/.cargo/env"
fi
export PATH="$HOME/.local/bin:$PATH"
command -v uv >/dev/null || { echo "❌ uv not found on PATH after install" >&2; exit 1; }

echo "⚡ [3/4] Synchronizing Python dependencies..."
uv sync

echo "🛠️ [4/4] Executing Ansible site playbook..."
uv run ansible-playbook site.yml --ask-become-pass

echo "✨ System bootstrap completed successfully!"
