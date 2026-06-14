# Dreame AC — Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
![status](https://img.shields.io/badge/status-alpha-red.svg)

Home Assistant integration for the **Dreame P-Wind10** air conditioner
(`dreame.aircon.tbl2528`, and potentially other Dreame AC models).

> **⚠️ Alpha:** This is an early alpha release. The MIoT property map (siid/piid)
> has been reverse-engineered for the P-Wind10 and may be incomplete or break on
> other models / firmware. Expect rough edges and breaking changes.

## How it works (please read)

This integration talks to the **Dreame cloud** (`iot.dreame.tech`), not to the
device on your local network. You sign in with your **Dreame app account**
(e-mail + password); the integration logs in, lists the air conditioners on your
account and controls them over the cloud RPC API.

- **`iot_class`: `cloud_polling`** — an internet connection and a reachable
  Dreame cloud are required. There is **no local-only mode**.
- Your account **e-mail and password are stored in the Home Assistant config
  entry** (standard HA behaviour) and are sent to the Dreame cloud to obtain an
  access token. They are **not** stored in this repository.
- The API uses fixed `Basic`-auth / salt constants extracted from the official
  Dreame app. These are **not personal credentials**; they may stop working when
  Dreame updates their app or backend.

## Account requirement: no "Sign in with…"

You need a **full Dreame account with an e-mail address and a password**.
Logins via **"Sign in with Apple"** or **"Sign in with Google"** are **not
supported** — those accounts have no password this integration can use.

If you only ever signed in socially: open the Dreame app, set an e-mail +
password on your account first, then use those credentials here.

## Features

- `climate` entity:
  - Power on/off
  - HVAC mode: **cool**, **dry**, **fan only** (cooling-only unit — no heat)
  - **Fan mode: low / high** (2 stages)
  - Target temperature (16–31 °C)
  - Current temperature (read-only)
  - Swing / oscillation on/off
- `switch` entity: **Nachtmodus** (night mode)
- **Change credentials without re-adding:** update your Dreame e-mail/password
  via the integration's **Configure** dialog. A re-authentication prompt also
  appears automatically if the stored login stops working.
- **Multiple air conditioners** on one account: if more than one is found during
  setup, you pick which to add; each becomes its own device and can be added
  separately.

## Installation via HACS

1. HACS → Integrations → ⋮ → Custom repositories
2. Add `https://github.com/patgits/hass-dreame-ac` — Category: **Integration**
3. Install "Dreame AC"
4. Restart Home Assistant

## Setup

1. Settings → Devices & Services → **Add Integration** → **Dreame AC**
2. Enter your **Dreame account e-mail and password** and pick your **server
   region** (the region you chose when creating the account, e.g. `eu`).
3. If your account has more than one air conditioner, **select the one** to add.
4. The air conditioner appears as a climate device with a night-mode switch.

To add a second air conditioner from the same account, run **Add Integration →
Dreame AC** again and pick the next device.

## How this scales

There is no shared backend: every user signs in with **their own** Dreame
account, and the integration only ever sees that account's devices. Scaling is
therefore per-user and automatic. The two real axes are:

- **More than one AC per account** — handled by the device-selection step above.
- **More models / firmware** — the property map in `const.py` is specific to
  `dreame.aircon.tbl2528`; other models need their own map (see Contributing).

## Contributing

The MIoT property map in `const.py` is specific to `dreame.aircon.tbl2528` and
may need adjustment for other models or firmware. Issues and PRs with property
dumps from other Dreame AC models are welcome.

## Supported Models

| Model | Status |
|-------|--------|
| Dreame P-Wind10 (`dreame.aircon.tbl2528`) | Alpha |

## License

MIT — see [LICENSE](LICENSE).
