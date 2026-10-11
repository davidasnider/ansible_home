# Network UPS Tools (NUT) Integration for macOS & Home Assistant

This document outlines the architecture, configuration, and operational procedures for integrating a Uninterruptible Power Supply (UPS) connected via USB to a Mac Studio into Home Assistant using Network UPS Tools (NUT).

## Architecture Overview

```
[UPS (e.g. CyberPower / APC)] --USB--> [Mac Studio (NUT Server: port 3493)]
                                                │
                                                ▼ (LAN query)
                                     [Home Assistant]
                                      (NUT Integration)
```

The Mac Studio acts as the **NUT Server** (`MODE=netserver`), hosting the driver (`macosx-ups`) and data server daemon (`upsd`). Home Assistant queries the Mac Studio across the local network on port `3493` to retrieve real-time telemetry (line voltage, battery level, runtime remaining, current load).

### Why the `macosx-ups` Driver on macOS?

On macOS, the operating system kernel and native power daemon (`/usr/libexec/ioupsd`) claim exclusive access to any attached USB HID UPS. Because of macOS security protections (IOKit/SIP), standard `libusb`-based drivers like `usbhid-ups` cannot detach the kernel driver and fail with:
```text
Can't claim USB device: Access denied (insufficient permissions)
```
NUT includes a native macOS meta-driver—**`macosx-ups`**—specifically built into Homebrew's NUT formula. This driver interfaces directly with Apple's `IOPowerSources` API, providing seamless access to UPS telemetry without requiring root privileges, kernel driver detaching, or competing with macOS power management.

## Ansible Automation

All configuration files, service daemons, and package installations are managed authoritatively via the `workstation` Ansible role:

* **Role Tasks:** `roles/workstation/tasks/nut-server-mac.yml` (invoked via `local-mac.yml`)
* **Role Defaults:** `roles/workstation/defaults/main.yml`

### Managed Configuration Files (`/opt/homebrew/etc/nut/`)

1. **`nut.conf`**: Configured with `MODE=netserver` to allow network-based monitoring.
2. **`ups.conf`**: Defines the hardware driver:
   ```ini
   [mac_ups]
   driver = macosx-ups
   port = auto
   desc = "Mac Studio UPS"
   pollinterval = 15
   ```
3. **`upsd.conf`**: Directs `upsd` to listen on a deliberately chosen address (loopback by default — see *Listener Binding* below):
   ```ini
   LISTEN 127.0.0.1 3493
   ```
4. **`upsd.users`**: Grants read-only access to the Home Assistant monitor (no `upsmon` role, since HA only polls data):
   ```ini
   [ha_monitor]
   password = <secure_password>
   ```
5. **`upsmon.conf`**: *Not managed.* Local `upsmon` shutdown orchestration is intentionally not configured — Home Assistant receives telemetry only, and no local monitor daemon runs on the Mac.

### LaunchAgent Background Daemon

A dedicated LaunchAgent is deployed to `~/Library/LaunchAgents/org.networkupstools.nut-server.plist` and managed via a runner script (`~/.local/bin/nut-server`). It:
* Starts the `macosx-ups` driver via `upsdrvctl start`.
* Runs `upsd -F` in the foreground so `launchd` manages process health and restarts it automatically.
* Operates without requiring `sudo`.

## Enabling on a Host

NUT server setup is **opt-in**: `workstation_nut_server_enabled` defaults to `false`, so a Mac without an attached UPS never starts the LaunchAgent (which would otherwise spin in an endless `KeepAlive` restart loop). Opt a specific host in via `host_vars`, e.g. `inventory/host_vars/<mac_studio_host>.yml`:

```yaml
---
workstation_nut_server_enabled: true
# Deliberately expose the service on the interface Home Assistant uses:
workstation_nut_listen_address: "<Mac_Studio_LAN_or_Tailscale_IP>"
```

(Or set the same variables in group vars for a `workstations` subgroup.)

## Configuration Variables

The following variables can be customized in inventory or host variables:

| Variable | Default Value | Description |
| --- | --- | --- |
| `workstation_nut_server_enabled` | `false` | Enables (per-host opt-in) or disables the NUT server setup |
| `workstation_nut_ups_name` | `mac_ups` | Name assigned to the UPS in NUT |
| `workstation_nut_ups_driver` | `macosx-ups` | Hardware driver (`macosx-ups` for native macOS support) |
| `workstation_nut_ups_port` | `auto` | Device port |
| `workstation_nut_ups_desc` | `Mac Studio UPS` | Description string |
| `workstation_nut_pollinterval` | `15` | Polling interval in seconds |
| `workstation_nut_listen_address` | `127.0.0.1` | IP address for the `upsd` listener (see *Listener Binding*) |
| `workstation_nut_listen_port` | `3493` | Port for `upsd` listener |
| `workstation_nut_ha_user` | `ha_monitor` | Monitoring username for Home Assistant |
| `workstation_nut_ha_password` | *(from env / 1Password — no weak default)* | Password for the Home Assistant monitor; the playbook fails early if none resolves |

To provide a custom password via the environment, export:
```bash
export NUT_HA_PASSWORD="<custom_secret>"
```
Or store it in 1Password under the title `Home Assistant NUT Password`. The role **fails early** if no password of at least 12 characters resolves, so a placeholder can never be written into `upsd.users`.

### Listener Binding

The listener binds to `127.0.0.1` by default — safe, but Home Assistant must run on the same machine. To let a remote Home Assistant instance connect:

* Set `workstation_nut_listen_address` to the **specific** LAN (or Tailscale) IP/hostname Home Assistant uses to reach this Mac — recommended.
* `0.0.0.0` should only be chosen deliberately: it exposes port 3493 on **every** interface (WAN, VPN, Tailscale) and therefore requires a strong per-deployment password (enforced by the fail-fast guard above).

## Verification & Service Management

### 1. Verification Script
The playbook creates a verification script at `~/.local/bin/nut-check`. It targets the configured listener address (`workstation_nut_listen_address`), so it works with both the default loopback binding and a LAN/Tailscale opt-in binding:
```bash
~/.local/bin/nut-check
```

### 2. Manual Testing (CLI)
To test driver communication directly, target the address `upsd` is bound to:
```bash
upsc mac_ups@127.0.0.1
```

> **Note:** `upsd` listens only on `workstation_nut_listen_address` (default `127.0.0.1`). If you opted a host in to a LAN or Tailscale IP for remote Home Assistant, `@localhost` will fail even though the service is healthy — substitute that address instead (e.g. `upsc mac_ups@<Mac_Studio_IP>`).

### 3. Service Lifecycle
The NUT server runs automatically under `launchd`. To view status or restart:
```bash
# Restart the service
launchctl kickstart -k gui/$(id -u)/org.networkupstools.nut-server

# View daemon logs
cat /opt/homebrew/var/log/nut-server.log
```

## Adding to Home Assistant

1. In Home Assistant, navigate to **Settings** > **Devices & Services** > **Add Integration**.
2. Search for **Network UPS Tools (NUT)**.
3. Enter the connection settings:
   * **Host:** `<Mac_Studio_IP>` (e.g. the Mac's LAN or Tailscale IP/hostname)
   * **Port:** `3493`
   * **Username:** `ha_monitor`
   * **Password:** *(the configured password)*
4. Home Assistant will discover the UPS and expose entities for:
   * Battery level (%)
   * Battery runtime (seconds / minutes)
   * Load percentage (%)
   * Input voltage (V)
   * Power status (`Online`, `On Battery`)

## macOS Energy Considerations

If the Mac Studio sleeps, the USB polling and NUT daemon pause, causing Home Assistant to lose live telemetry.

To prevent this:
1. Open macOS **System Settings** > **Energy**.
2. Ensure **Prevent automatic sleeping when the display is off** is enabled.
