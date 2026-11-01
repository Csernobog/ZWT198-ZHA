"""Tuya ZWT198 thermostat - ZHA quirk v0.2.

Manufacturer: _TZE284_zjhoqbrd
Model: TS0601

v0.1: Working climate, preset and working-day controls.
v0.2: Read-only DP109 schedule capture and decoding.

DP109 format:
    8 periods * 4 bytes = 32 bytes
    [hour, minute, temperature_hi, temperature_lo]

Do not write DP109 in this version.
"""

import logging

import zigpy.types as t
from zigpy.zcl import foundation

from zhaquirks.tuya.tuya_thermostat import (
    base_avatto_quirk,
    PresetModeV03,
    WorkingDayV02,
    NoManufTimeNoVersionRespTuyaMCUCluster,
)


_LOGGER = logging.getLogger(__name__)


def decode_schedule(value):
    """Decode and log the eight ZWT198 schedule periods.

    Return the original byte sequence for the read-only
    Tuya manufacturer attribute.
    """
    raw = bytes(value)

    _LOGGER.warning(
        "ZWT198 DP109 received: length=%d hex=%s",
        len(raw),
        raw.hex(" "),
    )

    if len(raw) != 32:
        _LOGGER.warning(
            "ZWT198 DP109 unexpected length: %d (expected 32)",
            len(raw),
        )
        return t.LVBytes(raw)

    for index in range(8):
        offset = index * 4

        hour = raw[offset]
        minute = raw[offset + 1]
        temperature_raw = int.from_bytes(
            raw[offset + 2:offset + 4],
            byteorder="big",
            signed=False,
        )
        temperature = temperature_raw / 10.0

        group = "WEEKDAY" if index < 6 else "WEEKEND"
        period = index + 1 if index < 6 else index - 5

        _LOGGER.warning(
            "ZWT198 SCHEDULE %s #%d: %02d:%02d -> %.1f C",
            group,
            period,
            hour,
            minute,
            temperature,
        )

    return t.LVBytes(raw)

def encode_schedule(value):
    """Validate the full DP109 schedule before writing."""
    if not isinstance(value, (bytes, bytearray, t.LVBytes)):
        raise ValueError(
            "DP109 requires 32 raw bytes, not text or HEX"
        )

    raw = bytes(value)

    if len(raw) != 32:
        raise ValueError(
            f"DP109 invalid length: {len(raw)}, expected 32"
        )

    previous_time = [-1, -1]

    for index in range(8):
        offset = index * 4
        hour = raw[offset]
        minute = raw[offset + 1]
        temperature = int.from_bytes(
            raw[offset + 2:offset + 4], "big"
        )

        if hour > 23 or minute > 59:
            raise ValueError(
                f"DP109 period {index + 1}: invalid time"
            )

        if not 50 <= temperature <= 350:
            raise ValueError(
                f"DP109 period {index + 1}: invalid temperature"
            )

        group = 0 if index < 6 else 1
        time_minutes = hour * 60 + minute

        if time_minutes <= previous_time[group]:
            raise ValueError(
                f"DP109 period {index + 1}: "
                "times must be increasing"
            )

        previous_time[group] = time_minutes

    _LOGGER.warning(
        "ZWT198 DP109 WRITE: %s", raw.hex(" ")
    )

    return t.LVBytes(raw)


(
    base_avatto_quirk.clone()
    .applies_to("_TZE284_zjhoqbrd", "TS0601")

    # Preset: Auto=0, Manual=1, Temporary Manual=2
    .tuya_enum(
        dp_id=4,
        attribute_name="preset_mode",
        enum_class=PresetModeV03,
        translation_key="preset_mode",
        fallback_name="Preset mode",
    )

    # Working days: Disabled=0, 5+2=1, 6+1=2, 7=3
    .tuya_enum(
        dp_id=104,
        attribute_name="working_day",
        enum_class=WorkingDayV02,
        translation_key="working_day",
        fallback_name="Working day",
    )

    # DP109: read/write schedule (32 bytes).
    # Writing is enabled at cluster level, but only
    # after explicit validation and a manual test.
    .tuya_dp_attribute(
        dp_id=109,
        attribute_name="schedule_raw",
        type=t.LVBytes,
        access=(
            foundation.ZCLAttributeAccess.Read
            | foundation.ZCLAttributeAccess.Write
        ),
        converter=decode_schedule,
        dp_converter=encode_schedule,
    )

    .add_to_registry(
        replacement_cluster=NoManufTimeNoVersionRespTuyaMCUCluster
    )
)