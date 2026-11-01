# ZWT198-ZHA

Custom ZHA thermostat support and weekly schedule editor for Tuya **ZWT198** (manufacturer `_TZE284_zjhoqbrd`, Zigbee model `TS0601`).

> **v0.4 development scaffold.** The thermostat, RAW DP109 program write, Pyscript helpers and expandable Lovelace schedule graph were tested locally on 2026-11-01. The exact, verified local quirk/Pyscript/dashboard source still needs to be imported. **This repository is not yet a complete installable release.**

## Verified features

- ZHA thermostat control, Manual / Auto and heating status
- DP109 weekly schedule: 6 weekday slots + 2 weekend slots, RAW 32 bytes
- Schedule load and save from Home Assistant helpers
- Real-device verification of edited schedule entries
- Automatic load on slot change with short debounce
- Lovelace expandable weekly editor with switchable weekday/weekend ApexCharts step graph

## Repository structure

```text
custom_zha_quirks/      # quirk destination (verified file pending)
pyscript/               # editor services (verified file pending)
packages/
  ZWT198_helpers.yaml   # HA helpers
lovelace/               # tested dashboard YAML pending
docs/
  installation.md       # setup and validation
  protocol.md           # DP map and 32-byte DP109 format
  development.md        # v0.3 / v0.4 progress
  limitations.md        # known issues and safety
  screenshots/          # images pending
```

Start with [installation instructions](docs/installation.md), [protocol details](docs/protocol.md), and [development log](docs/development.md).

## Known limitation

The current Pyscript send path uses a Tuya RAW MCU command with `expect_reply=False`. Chart refresh after save is optimistic; a fresh matching DP109 device report and a write lock remain on the roadmap. Check the physical thermostat after editing.

## Tested environment

Home Assistant Core 2026.10.2, ZHA 2.3.1, zha-quirks 2.3.0, Python 3.14.6.

## Licensing

License not yet selected; repository visibility does not itself grant reuse rights.
