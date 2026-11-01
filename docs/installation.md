# Installation / telepítés

> **Not a complete installation package yet.** Before following these instructions, import the already-tested local `tuya_ts0601_zjhoqbrd.py`, `zwt198_schedule.py` and Lovelace card YAML. Do not substitute reconstructed code for the known-good versions.

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
| `custom_zha_quirks/tuya_ts0601_zjhoqbrd.py` (pending) | `/config/custom_zha_quirks/tuya_ts0601_zjhoqbrd.py` |
| `pyscript/zwt198_schedule.py` (pending) | `/config/pyscript/zwt198_schedule.py` |
| `packages/ZWT198_helpers.yaml` | `/config/ZWT198_helpers.yaml` |
| `lovelace/zwt198_editor.yaml` (pending) | Lovelace YAML editor |

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

The original local test referenced an installation-specific device IEEE address and helper IDs. Future releases must make the IEEE and entity IDs configurable. Never publish the local IEEE as a public default.
