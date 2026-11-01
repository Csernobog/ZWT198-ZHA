# ZWT198-ZHA

Custom ZHA thermostat support and weekly schedule editor for Tuya **ZWT198** (manufacturer `_TZE284_zjhoqbrd`, Zigbee model `TS0601`).

> **v0.4 tested local snapshot.** The quirk, Pyscript and Lovelace YAML are now included from the user's working installation. The Pyscript IEEE address is replaced with a placeholder; edit it before deployment. This remains a device-specific development release, not yet a fully generalized integration.

## Verified features

- ZHA thermostat control, Manual / Auto and heating status
- DP109 weekly schedule: 6 weekday slots + 2 weekend slots, RAW 32 bytes
- Schedule load and save from Home Assistant helpers
- Real-device verification of edited schedule entries
- Automatic load on slot change with short debounce
- Lovelace expandable weekly editor with switchable weekday/weekend ApexCharts step graph

## Repository structure

```text
custom_zha_quirks/      # tested quirk source
pyscript/               # tested editor services
packages/
  ZWT198_helpers.yaml   # HA helpers
lovelace/               # tested expandable dashboard YAML
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
