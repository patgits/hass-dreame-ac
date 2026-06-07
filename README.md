# Dreame AC — Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

Home Assistant integration for the **Dreame P-Wind10** air conditioner
(`dreame.aircon.tbl2528`, and potentially other Dreame AC models).

> **Status:** Early development — the MIoT property map (siid/piid) has been
> reverse-engineered for the P-Wind10 and may need adjustment for other models
> or firmware versions.

## How it works (please read)

This integration talks to the **Dreame cloud** (`iot.dreame.tech`), not to the
device on your local network. You sign in with your **Dreame app account**
(e-mail + password); the integration logs in, finds your air conditioner
automatically and polls/controls it over the cloud RPC API.

- **`iot_class`: `cloud_polling`** — an internet connection and a reachable
  Dreame cloud are required.
- Your account **e-mail and password are stored in the Home Assistant config
  entry** (standard HA behaviour) and are sent to the Dreame cloud to obtain an
  access token. They are **not** stored in this repository.
- The API uses fixed `Basic`-auth / salt constants extracted from the official
  Dreame app. These are **not personal credentials**; they may stop working when
  Dreame updates their app or backend.

There is **no local-only mode** in this integration.

## Features

- `climate` entity:
  - Power on/off
  - HVAC mode: **cool**, **dry**, **fan only** (cooling-only unit — no heat)
  - Target temperature (16–31 °C)
  - Current temperature (read-only)
  - Swing / oscillation on/off
- `switch` entity: **Nachtmodus** (night mode)

> **Note:** Fan speed is **not** exposed over the Dreame cloud RPC for this
> model and is therefore not available.

## Installation via HACS

1. HACS → Integrations → ⋮ → Custom repositories
2. Add `https://github.com/patgits/hass-dreame-ac` — Category: **Integration**
3. Install "Dreame AC"
4. Restart Home Assistant
5. Settings → Devices & Services → Add Integration → **Dreame AC**
6. Enter your **Dreame account** e-mail, password and server region

## Contributing

The MIoT property map in `const.py` is specific to `dreame.aircon.tbl2528` and
may need adjustment for other models or firmware. Issues and PRs with property
dumps from other Dreame AC models are welcome.

## Supported Models

| Model | Status |
|-------|--------|
| Dreame P-Wind10 (`dreame.aircon.tbl2528`) | In development |
