# Dreame AC — Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

Home Assistant integration for the **Dreame P-Wind10** air conditioner (and potentially other Dreame AC models).

> **Status:** Early development — MIoT property map (siid/piid) is being verified against the real device.

## Features

- Full `climate` entity: power, HVAC mode, target temperature, fan speed, swing
- Local connection (IP + Token) — no cloud dependency
- Xiaomi Cloud fallback for token-free setup

## Installation via HACS

1. HACS → Integrations → ⋮ → Custom repositories
2. Add `https://github.com/patgits/hass-dreame-ac` — Category: **Integration**
3. Install "Dreame AC"
4. Restart Home Assistant
5. Settings → Devices & Services → Add Integration → **Dreame AC**

## Local Setup: Get your Token

```bash
pip install python-miio
miiocli discover --handshake 1
```

The token is a 32-character hex string. It never leaves your local network when using local mode.

## Contributing

The MIoT property map in `const.py` may need adjustment for your device firmware.  
Run this to dump all properties from your device:

```bash
miiocli device --ip <IP> --token <TOKEN> get_properties_for_mapping
```

Open an issue or PR with the output.

## Supported Models

| Model | Status |
|-------|--------|
| Dreame P-Wind10 | In development |
