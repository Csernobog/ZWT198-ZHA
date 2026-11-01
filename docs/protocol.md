# ZWT198 Tuya datapoint protocol — engineering notes

**Device identification:** manufacturer `_TZE284_zjhoqbrd`; Zigbee model `TS0601`. Vendor-specific Tuya MCU cluster: endpoint **1**, cluster **0xEF00**.

The base quirk was built by cloning an existing Avatto quirk and customizing the following mappings.

| DP | Purpose | Notes |
|---:|---|---|
| 1 | power / heat-off control | supported locally |
| 2 | target temperature | supported locally |
| 3 | measured temperature | supported locally |
| 4 | preset mode | Manual / Auto |
| 15 | maximum temperature limit | entity observed |
| 19 | temperature offset | calibration |
| 101 | heating state | heating / idle |
| 104 | working-day arrangement | 5+2, 6+1, 7 |
| 107 | deadzone / hysteresis | not sensor calibration |
| **109** | **weekly schedule** | **32-byte RAW payload** |

## DP109 payload

Exactly **8 periods × 4 bytes = 32 bytes**.

```text
[hour, minute, temperature_hi, temperature_lo] × 8
```

Temperature is an unsigned big-endian integer in units of **0.1 °C**. First 6 periods represent the weekday program; last 2 represent the weekend program.

Example readback (8 periods):

```text
06 28 00 d2  08 00 00 a0  0b 1e 00 a0  0c 1e 00 aa
11 00 00 dc  16 00 00 a0  08 00 00 dc  17 00 00 a0
```

Decoded:

| Slot | Time | Target |
|---|---|---|
| Weekday 1 | 06:40 | 21.0 °C |
| Weekday 2 | 08:00 | 16.0 °C |
| Weekday 3 | 11:30 | 16.0 °C |
| Weekday 4 | 12:30 | 17.0 °C |
| Weekday 5 | 17:00 | 22.0 °C |
| Weekday 6 | 22:00 | 16.0 °C |
| Weekend 1 | 08:00 | 22.0 °C |
| Weekend 2 | 23:00 | 16.0 °C |

This is an **example from local testing**, not factory default.

## Read/write behavior

The tested quirk stores the decoded raw program in `schedule_raw`, an `LVBytes` attribute (attribute ID `0xEF6D`, decimal 109).

**Important:** ordinary ZHA `cluster.write_attributes({"schedule_raw": ...})` did **not** work with the local environment. The ZHA layer tried to coerce `TuyaClusterData.attr_value` into an integer, raised an exception, and the attribute cache could nonetheless change. Do not treat cache changes as device acknowledgement.

The verified transmit path constructs a Tuya MCU `TuyaData` with `TuyaDPType.RAW`, `LVBytes(updated_32_bytes)`, wraps it in `TuyaDatapointData(dp=109, ...)`, then `TuyaCommand(status=0, tsn=..., datapoints=[...])` and calls `cluster.command(cluster.mcu_write_command, command, expect_reply=False, manufacturer=None)`.

One local write was confirmed on the physical thermostat: weekday slot 1 changed to **06:40 / 21.0 °C**. Another UI-level test confirmed an updated **06:00** slot.

## Schedule validation

Before writing, verify:
- Exactly 32 payload bytes
- Valid hour and minute for each period
- Strictly increasing times within each day group, weekday slots 1–6 and weekend slots 1–2
- Target temperatures in the tested range 5–35 °C
- Preserve unchanged periods; send the complete 32-byte DP109 payload

## Physical thermostat

In OFF state, the **M + down arrow** key combination opens a configuration menu. Local device controls allow editing all 6 weekday and 2 weekend slots. Its clock/day handling worked without Home Assistant.

## Pending protocol validation

The present `expect_reply=False` transport is send-only; a `None` return is not a confirmed ACK. Production-level write confirmation should wait for a **fresh, matching DP109 report from the device**, with timeout and collision control.
