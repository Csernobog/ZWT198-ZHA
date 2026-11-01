# Installation / telepítés

> **Verified v0.4 files are included.** Set your own Zigbee device IEEE in `pyscript/zwt198_schedule.py` before deployment. The dashboard climate entity ID may also need adapting. Make a backup before replacing local working files.

## Tested environment (2026-11-01)

- Home Assistant OS on Raspberry Pi
- Home Assistant Core **2026.10.2**
- ZHA **2.3.1**
- zha-quirks **2.3.0**
- Python **3.14.6**
- Pyscript with relevant imports available

## Files

| Repository | Home Assistant destination |
|---|---|
| `custom_zha_quirks/tuya_ts0601_zjhoqbrd.py` | `/config/custom_zha_quirks/tuya_ts0601_zjhoqbrd.py` |
| `pyscript/zwt198_schedule.py` | `/config/pyscript/zwt198_schedule.py` |
| `packages/ZWT198_helpers.yaml` | `/config/ZWT198_helpers.yaml` |
| `lovelace/zwt198_editor.yaml` | Lovelace YAML editor |

Configure the ZHA quirk path in `configuration.yaml` (merge into existing `zha:` configuration, do not duplicate top-level keys):

```yaml
zha:
  enable_quirks: true
  custom_quirks_path: /config/custom_zha_quirks/
```

Load the helper package from your existing `homeassistant:` configuration:

```yaml
homeassistant:
  packages:
    zwt198: !include ZWT198_helpers.yaml
```

Do not add a second `homeassistant:` key if one already exists.

The editor depends on Pyscript and the dashboard uses a custom **ApexCharts Card**. The tested dashboard also uses an **Expander Card**.

## Validate

1. Back up the current working Home Assistant configuration.
2. Copy the **verified** quirk, restart HA as required, and check device entities.
3. Import the helper package and confirm the three helper entities exist.
4. Import the working Pyscript, reload Pyscript, and verify `pyscript.zwt198_schedule_load` and `pyscript.zwt198_schedule_save`.
5. Load weekday slot 1 and verify values on the thermostat.
6. Change a single slot, save, and verify on the physical display.
7. Add the Lovelace card and verify weekday/weekend graph switching.

### Portability still required

The included Pyscript has `IEEE = "REPLACE_WITH_YOUR_DEVICE_IEEE"`; set this to your own device IEEE. The included Lovelace card has a deployment-specific climate entity ID to update. The original local test referenced installation-specific helper IDs. Future releases must make the IEEE and entity IDs configurable. Never publish the local IEEE as a public default.
