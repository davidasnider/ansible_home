# Network UPS Tools (NUT) Integration

A USB UPS is attached to the Raspberry Pi `bedroom-pi`, which runs the NUT server. Home Assistant reads UPS telemetry from it, and the Mac Studio runs a NUT client so it shuts down cleanly when power is lost.

## Architecture

```
[UPS] --USB--> [bedroom-pi: NUT server (upsd :3493) + upsmon primary]
                        │
          ┌─────────────┴──────────────┐
          ▼ (LAN, 10.1.1.0/24)         ▼ (LAN)
 [Home Assistant]               [Mac Studio: upsmon secondary]
  (NUT integration, read-only)   (shuts down on low battery / FSD)
```

* **bedroom-pi** (`nut_server` role) drives the UPS with `usbhid-ups` and serves `upsd` on port `3493`. Its local `upsmon` is the **primary**, so it declares the forced shutdown (FSD) and powers off last.
* **Home Assistant** polls through a read-only `ha_monitor` account.
* **Mac Studio** (`workstation` role) runs `upsmon` as a **secondary** under a root LaunchDaemon, so it can run `shutdown` when the server reports a low battery or FSD.

## Ansible Automation

| Piece | Location |
| --- | --- |
| Server role | `roles/nut_server/` (applied to the `nut_servers` inventory group in `playbooks/raspberry_pis.yml`) |
| Client tasks | `roles/workstation/tasks/nut-client-mac.yml` (included by `local-mac.yml`) |
| Opt-in flags | `nut_servers` group in `inventory/hosts.yml`; `workstation_nut_client_enabled` on `localhost` |

### Passwords

Each secret resolves once per run, from an environment variable first and then 1Password. The roles fail early if one is shorter than 12 characters.

| 1Password item (field `password`) | Environment variable | Account | Used by |
| --- | --- | --- | --- |
| `Home Assistant NUT Password` | `NUT_HA_PASSWORD` | `ha_monitor` (read-only) | Home Assistant |
| `NUT Primary Password` | `NUT_PRIMARY_PASSWORD` | `upsmon_primary` (`upsmon primary`) | upsmon on the Pi |
| `NUT Secondary Password` | `NUT_SECONDARY_PASSWORD` | `upsmon_secondary` (`upsmon secondary`) | upsmon on the Mac |

Create the three items in 1Password before the first run.

### Server configuration (`/etc/nut/` on the Pi)

* `nut.conf`: `MODE=netserver`
* `ups.conf`: `[ups]` with `driver = usbhid-ups`, `port = auto`
* `upsd.conf`: `LISTEN 0.0.0.0 3493`
* `upsd.users`: the three accounts above
* `upsmon.conf`: `MONITOR ups@localhost 1 upsmon_primary <password> primary`

UFW allows port `3493` only from `nut_server_allowed_cidr` (default `10.1.1.0/24`); the rest of the Pi stays on the baseline firewall policy.

### Client configuration (`/opt/homebrew/etc/nut/` on the Mac)

* `nut.conf`: `MODE=netclient`
* `upsmon.conf` (root-only, `0600`): `MONITOR ups@bedroom-pi.thesniderpad.com:3493 1 upsmon_secondary <password> secondary`, `SHUTDOWNCMD "/sbin/shutdown -h +0"`
* `/Library/LaunchDaemons/org.networkupstools.upsmon.plist` runs `upsmon -F` at boot and restarts it if it exits.

The Mac tasks that need root use `become`, so run the playbook with `--ask-become-pass`. The same run removes the old Mac-hosted server (LaunchAgent, runner script, `ups.conf`, `upsd.conf`, `upsd.users`).

## Variables

| Variable | Default | Description |
| --- | --- | --- |
| `nut_server_ups_name` | `ups` | UPS name in NUT |
| `nut_server_ups_driver` | `usbhid-ups` | Driver |
| `nut_server_ups_desc` | `Bedroom UPS` | Description |
| `nut_server_pollinterval` | `15` | Poll interval (seconds) |
| `nut_server_listen_address` / `_port` | `0.0.0.0` / `3493` | `upsd` listener |
| `nut_server_allowed_cidr` | `10.1.1.0/24` | Source network allowed through UFW |
| `workstation_nut_client_enabled` | `false` | Enable the Mac NUT client (per-host opt-in) |
| `workstation_nut_server_host` | `bedroom-pi.thesniderpad.com` | NUT server the Mac monitors |
| `workstation_nut_ups_name` | `ups` | UPS name on the server |

## Running

```bash
# Pi: install and configure the server
uv run ansible-playbook -i inventory/hosts.yml --limit bedroom-pi site.yml

# Mac: switch to the client and remove the old server
uv run ansible-playbook -i inventory/hosts.yml --limit localhost site.yml --ask-become-pass
```

## Verification

```bash
# On the Pi
upsc ups@localhost
systemctl status nut-server nut-monitor

# From the Mac (also installed as ~/.local/bin/nut-check)
upsc ups@bedroom-pi.thesniderpad.com
sudo launchctl print system/org.networkupstools.upsmon
tail /opt/homebrew/var/log/upsmon.log
```

## Home Assistant

Update the existing NUT integration (**Settings** > **Devices & Services** > **Network UPS Tools**) to point at the Pi:

* **Host:** `bedroom-pi.thesniderpad.com` (or `10.1.1.249`)
* **Port:** `3493`
* **Username:** `ha_monitor`
* **Password:** the `Home Assistant NUT Password` value

The UPS name changed from `mac_ups` to `ups`, so entity IDs may change. Re-select the UPS in the integration if it is not picked up automatically.
