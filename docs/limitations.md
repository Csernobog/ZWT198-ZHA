# Limitations and known caveats

1. **Source included, installation-specific placeholders remain.** Configure your device IEEE in the Pyscript file and climate entity ID in the Lovelace YAML before use.
2. **Only one device variant tested.** `_TZE284_zjhoqbrd` / `TS0601` should not be broadened to all TS0601 devices.
3. **Write confirmation pending.** `expect_reply=False` returns after dispatch without ensuring that the thermostat accepted and stored DP109.
4. **Optimistic chart update.** Immediately after save, the graph may display the requested state before a matching device report arrives.
5. **Rapid UI interaction.** A short debounce improved fast slot-selection behavior locally; this does not replace robust write serialization and fresh-report readback.
6. **Home Assistant-specific details.** The initial implementation contains deployment-specific identifiers that must be parameterized before a general-purpose release.
7. **Thermal control caution.** Keep the physical thermostat available to verify and recover settings.
