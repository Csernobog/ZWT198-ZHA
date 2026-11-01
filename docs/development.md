# Development log

## v0.3 — quirk and protocol access (2026-11-01 snapshot)

- Reused a working ZHA Avatto quirk as a base, specialized to `_TZE284_zjhoqbrd` / `TS0601`.
- Fixed preset mode / working-day mappings.
- Identified the weekly program as Tuya DP109 and decoded all eight four-byte periods.
- Verified physical program changes are reported to ZHA.
- Discovered that generic `write_attributes` does not reliably transmit DP109 RAW and can produce misleading cache contents.
- Successfully transmitted the complete schedule via a native Tuya RAW MCU command and verified on the thermostat.

## v0.4 — working GUI editor (2026-11-01)

- Added three HA helpers: slot, time, target temperature.
- Added Pyscript load/save services.
- Added auto-load on slot selection with ~300 ms debounce to reduce rapid-navigation races.
- Added a Lovelace editor and expandable UI.
- Added ApexCharts step profiles for weekday and weekend, including automatic selection-dependent card switching.
- Added chart refresh after writes. **Current refresh is optimistic** (requested program), not a fresh device-confirmed report.
- Verified a UI-driven write on the physical thermostat.

## Next work

1. Import exact source snapshots (quirk, Pyscript, working dashboard YAML) from the tested Home Assistant system.
2. Remove hard-coded per-installation identifiers.
3. Add report-based write confirmation, timeout, and second-write lock.
4. Add testing/documentation for additional firmware variants.
5. Choose a license and publish an installable release only after validating the committed source.
