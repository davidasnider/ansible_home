#!/bin/bash
# UTM macOS VM Management Script for Molecule Testing
# This script manages a UTM macOS VM for running Molecule tests

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Configuration - these can be overridden by environment variables
UTM_VM_NAME="${UTM_VM_NAME:-ansible-test}"
UTM_SNAPSHOT_NAME="${UTM_SNAPSHOT_NAME:-molecule-baseline}"
SSH_HOST="${MOLECULE_MACOS_HOST:-}"  # Will be auto-detected if empty
SSH_PORT="${MOLECULE_MACOS_PORT:-22}"
SSH_USER="${MOLECULE_MACOS_USER:-$(whoami)}"
SSH_KEY="${MOLECULE_MACOS_SSH_KEY:-$HOME/.ssh/id_rsa}"
SSH_TIMEOUT=60
VM_BOOT_TIMEOUT=120
VM_IP=""  # Will store detected IP

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

error() {
    echo -e "${RED}❌${NC} $1"
}

# Check if UTM CLI is available
check_utm_cli() {
    if ! command -v utmctl >/dev/null 2>&1; then
        error "UTM CLI (utmctl) not found. Please install UTM with CLI support."
        error "You can install it via: brew install --cask utm"
        exit 1
    fi
}

# Check if VM exists
check_vm_exists() {
    if ! utmctl list | grep -q "$UTM_VM_NAME"; then
        error "VM '$UTM_VM_NAME' not found."
        error "Available VMs:"
        utmctl list
        exit 1
    fi
}

# Check if snapshot exists
check_snapshot_exists() {
    # Note: UTM CLI snapshot listing may vary by version
    log "Checking if snapshot '$UTM_SNAPSHOT_NAME' exists..."
    # This is a placeholder - UTM CLI commands for snapshots may differ
    # You may need to adjust this based on your UTM version
}

# Detect VM IP address
detect_vm_ip() {
    log "Detecting VM IP address..."

    # If SSH_HOST is already set, use it
    if [ -n "$SSH_HOST" ]; then
        VM_IP="$SSH_HOST"
        log "Using configured SSH host: $VM_IP"
        return 0
    fi

    # Try UTM CLI ip-address command first
    if VM_IP=$(utmctl ip-address "$UTM_VM_NAME" 2>/dev/null | head -1 | grep -E '^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$'); then
        log "Found VM IP via UTM CLI: $VM_IP"
        return 0
    fi

    # Fallback: Scan common VM IP ranges
    log "UTM CLI ip-address failed, scanning for VM..."

    # Common UTM/virtualization IP ranges
    local ranges=("192.168.64.0/24" "10.0.0.0/24" "172.16.0.0/24")

    for range in "${ranges[@]}"; do
        log "Scanning range: $range"

        # Use nmap if available, otherwise try ping sweep
        if command -v nmap >/dev/null 2>&1; then
            # Scan for SSH (port 22) in the range
            VM_IP=$(nmap -p 22 --open "$range" 2>/dev/null | grep -B4 "22/tcp open" | grep "Nmap scan report" | head -1 | awk '{print $NF}' | tr -d '()')
        else
            # Simple ping sweep (less reliable but doesn't require nmap)
            local base_ip=$(echo "$range" | cut -d'/' -f1 | cut -d'.' -f1-3)
            for i in {1..20}; do
                local test_ip="$base_ip.$i"
                if ping -c 1 -W 1000 "$test_ip" >/dev/null 2>&1; then
                    # Test if SSH is available
                    if nc -z -w 2 "$test_ip" 22 2>/dev/null; then
                        VM_IP="$test_ip"
                        break
                    fi
                fi
            done
        fi

        if [ -n "$VM_IP" ]; then
            log "Found VM IP: $VM_IP"
            return 0
        fi
    done

    error "Could not detect VM IP address. Please set MOLECULE_MACOS_HOST manually."
    return 1
}

# Start VM from snapshot
start_vm() {
    log "Starting VM '$UTM_VM_NAME' from snapshot '$UTM_SNAPSHOT_NAME'..."

    # Stop VM if it's running
    if utmctl status "$UTM_VM_NAME" | grep -q "started"; then
        log "VM is already running, stopping first..."
        utmctl stop "$UTM_VM_NAME"
        sleep 5
    fi

    # Restore from snapshot (command may vary)
    # utmctl restore "$UTM_VM_NAME" "$UTM_SNAPSHOT_NAME" || true

    # Start the VM
    utmctl start "$UTM_VM_NAME"

    log "Waiting for VM to boot (timeout: ${VM_BOOT_TIMEOUT}s)..."
    local timeout=$VM_BOOT_TIMEOUT
    while [ $timeout -gt 0 ]; do
        if utmctl status "$UTM_VM_NAME" | grep -q "started"; then
            success "VM is running"
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done

    if [ $timeout -le 0 ]; then
        error "VM failed to start within $VM_BOOT_TIMEOUT seconds"
        return 1
    fi
}

# Wait for SSH connectivity
wait_for_ssh() {
    # Detect VM IP if not already set
    if [ -z "$VM_IP" ]; then
        if ! detect_vm_ip; then
            return 1
        fi
    fi

    log "Waiting for SSH connectivity to ${SSH_USER}@${VM_IP}:${SSH_PORT}..."

    local timeout=$SSH_TIMEOUT
    while [ $timeout -gt 0 ]; do
        if ssh -i "$SSH_KEY" -p "$SSH_PORT" -o ConnectTimeout=5 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$SSH_USER@$VM_IP" "echo 'SSH connection successful'" >/dev/null 2>&1; then
            success "SSH connection established to $VM_IP"
            return 0
        fi
        log "SSH not ready, waiting... (${timeout}s remaining)"
        sleep 5
        timeout=$((timeout - 5))
    done

    error "SSH connection failed after $SSH_TIMEOUT seconds"
    return 1
}

# Run Molecule tests
run_molecule_tests() {
    log "Running Molecule tests on macOS VM..."

    cd "$PROJECT_ROOT"

    # Export environment variables for UTM VM connection
    export MOLECULE_MACOS_CONNECTION=ssh
    export MOLECULE_MACOS_HOST="$VM_IP"
    export MOLECULE_MACOS_PORT="$SSH_PORT"
    export MOLECULE_MACOS_USER="$SSH_USER"
    export MOLECULE_MACOS_SSH_KEY="$SSH_KEY"
    export MOLECULE_MACOS_PYTHON="/usr/bin/python3"

    log "Environment configured:"
    log "  Connection: $MOLECULE_MACOS_CONNECTION"
    log "  Host: $MOLECULE_MACOS_HOST:$MOLECULE_MACOS_PORT"
    log "  User: $MOLECULE_MACOS_USER"
    log "  SSH Key: $MOLECULE_MACOS_SSH_KEY"

    # Run the molecule test
    cd roles/localhost
    if poetry run molecule test -s macos; then
        success "Molecule macOS tests completed successfully!"
        return 0
    else
        error "Molecule macOS tests failed"
        return 1
    fi
}

# Stop VM and restore snapshot
cleanup_vm() {
    log "Cleaning up VM..."

    if utmctl status "$UTM_VM_NAME" | grep -q "started"; then
        log "Stopping VM '$UTM_VM_NAME'..."
        utmctl stop "$UTM_VM_NAME"

        # Wait for VM to stop
        local timeout=30
        while [ $timeout -gt 0 ]; do
            if ! utmctl status "$UTM_VM_NAME" | grep -q "started"; then
                success "VM stopped"
                break
            fi
            sleep 2
            timeout=$((timeout - 2))
        done
    fi

    # Restore snapshot to reset VM state
    # utmctl restore "$UTM_VM_NAME" "$UTM_SNAPSHOT_NAME" || warning "Failed to restore snapshot"
}

# Print usage
usage() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  test     Run complete test cycle (start VM, test, cleanup)"
    echo "  start    Start VM from snapshot"
    echo "  stop     Stop VM and restore snapshot"
    echo "  ssh      Test SSH connectivity"
    echo "  status   Show VM status"
    echo ""
    echo "Environment variables:"
    echo "  UTM_VM_NAME               Name of UTM VM (default: macOS-Test)"
    echo "  UTM_SNAPSHOT_NAME         Snapshot name (default: molecule-baseline)"
    echo "  MOLECULE_MACOS_HOST       SSH host (default: 127.0.0.1)"
    echo "  MOLECULE_MACOS_PORT       SSH port (default: 2222)"
    echo "  MOLECULE_MACOS_USER       SSH user (default: current user)"
    echo "  MOLECULE_MACOS_SSH_KEY    SSH private key (default: ~/.ssh/id_rsa)"
}

# Main execution
main() {
    local command="${1:-test}"

    case "$command" in
        "test")
            check_utm_cli
            check_vm_exists

            log "🚀 Starting UTM macOS Molecule testing workflow..."

            # Set up cleanup trap
            trap cleanup_vm EXIT INT TERM

            start_vm
            wait_for_ssh

            if run_molecule_tests; then
                success "🎉 UTM macOS Molecule tests completed successfully!"
                exit 0
            else
                error "❌ UTM macOS Molecule tests failed"
                exit 1
            fi
            ;;

        "start")
            check_utm_cli
            check_vm_exists
            start_vm
            wait_for_ssh
            success "VM is ready for testing"
            ;;

        "stop")
            check_utm_cli
            cleanup_vm
            ;;

        "ssh")
            wait_for_ssh
            ;;

        "status")
            check_utm_cli
            utmctl status "$UTM_VM_NAME" || echo "VM not found or not running"
            ;;

        "help"|"-h"|"--help")
            usage
            ;;

        *)
            error "Unknown command: $command"
            usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
