

"""ZWT198 weekly schedule editor v0.4.

Uses confirmed ZHA Tuya RAW DP109 command path.
Edits one of eight periods at a time.
"""

from homeassistant.components.zha.helpers import get_zha_gateway
from zigpy.types import EUI64, LVBytes

from zhaquirks.tuya import (
    TuyaData,
    TuyaDPType,
    TuyaDatapointData,
    TuyaCommand,
)

IEEE = "REPLACE_WITH_YOUR_DEVICE_IEEE"

SLOTS = [
    "Hétköznap 1",
    "Hétköznap 2",
    "Hétköznap 3",
    "Hétköznap 4",
    "Hétköznap 5",
    "Hétköznap 6",
    "Hétvége 1",
    "Hétvége 2",
]


def get_cluster():
    gateway = get_zha_gateway(hass)
    device = gateway.application_controller.get_device(
        EUI64.convert(IEEE)
    )
    cluster = device.endpoints[1].in_clusters[0xEF00]
    return device, cluster


def get_schedule(cluster):
    value = cluster.get("schedule_raw")

    if value is None:
        raise ValueError("DP109 cache is empty")

    raw = bytes(value)

    if len(raw) != 32:
        raise ValueError("DP109 must be 32 bytes")

    return raw


def selected_slot():
    name = hass.states.get(
        "input_select.zwt198_programhely"
    ).state
    return SLOTS.index(name)


def decode_period(raw, index):
    offset = index * 4

    hour = raw[offset]
    minute = raw[offset + 1]
    temperature = int.from_bytes(
        raw[offset + 2:offset + 4], "big"
    ) / 10.0

    return hour, minute, temperature

def update_schedule_chart(raw):
    """Publish the complete DP109 schedule for ApexCharts."""
    periods = []

    for i in range(8):
        hour, minute, temperature = decode_period(raw, i)
        periods.append({
            "time": f"{hour:02d}:{minute:02d}",
            "temperature": temperature,
        })

    state.set(
        "pyscript.zwt198_schedule",
        "ready",
        weekday=periods[:6],
        weekend=periods[6:],
    )
    
def validate_schedule(raw):
    if len(raw) != 32:
        raise ValueError("Invalid DP109 length")

    for group in (range(6), range(6, 8)):
        previous = -1

        for index in group:
            hour, minute, temp = decode_period(
                raw, index
            )

            if hour > 23 or minute > 59:
                raise ValueError("Invalid time")

            if not 5 <= temp <= 35:
                raise ValueError("Invalid temperature")

            current = hour * 60 + minute

            if current <= previous:
                raise ValueError(
                    "Schedule times must be increasing"
                )

            previous = current


@service
async def zwt198_schedule_load():
    """Load selected period into HA helpers."""

    device, cluster = get_cluster()
    raw = get_schedule(cluster)
    validate_schedule(raw)
    
    # Publish the entire DP109 schedule for the chart.
    
    update_schedule_chart(raw)

    index = selected_slot()
    hour, minute, temp = decode_period(raw, index)

    await hass.services.async_call(
        "input_datetime",
        "set_datetime",
        {
            "entity_id": "input_datetime.zwt198_idopont",
            "time": f"{hour:02d}:{minute:02d}:00",
        },
        blocking=True,
    )

    await hass.services.async_call(
        "input_number",
        "set_value",
        {
            "entity_id": "input_number.zwt198_homerseklet",
            "value": temp,
        },
        blocking=True,
    )

    # Save the exact source snapshot for conflict checking.
    state.set(
        "pyscript.zwt198_editor_snapshot",
        raw.hex(),
        slot=index,
    )

    log.warning(
        "ZWT198 EDITOR LOAD #%d: %02d:%02d %.1f C",
        index + 1, hour, minute, temp
    )


@service
async def zwt198_schedule_save():
    """Write one edited period using RAW DP109."""

    device, cluster = get_cluster()
    current = get_schedule(cluster)
    index = selected_slot()

    snapshot = hass.states.get(
        "pyscript.zwt198_editor_snapshot"
    )

    if snapshot is None or snapshot.state != current.hex():
        raise ValueError(
            "Schedule changed since load; reload first"
        )

    if int(snapshot.attributes["slot"]) != index:
        raise ValueError(
            "Selected slot changed; reload first"
        )

    time_value = hass.states.get(
        "input_datetime.zwt198_idopont"
    ).state

    hour, minute = map(
        int, time_value.split(":")[:2]
    )

    temp = float(
        hass.states.get(
            "input_number.zwt198_homerseklet"
        ).state
    )

    if not 0 <= hour <= 23 or not 0 <= minute <= 59:
        raise ValueError("Invalid time")

    if not 5 <= temp <= 35:
        raise ValueError("Invalid temperature")

    if abs(temp * 2 - round(temp * 2)) > 0.0001:
        raise ValueError("Temperature must use 0.5 C steps")

    temp_raw = round(temp * 10)

    updated = bytearray(current)
    offset = index * 4

    updated[offset:offset + 4] = bytes([
        hour,
        minute,
        (temp_raw >> 8) & 0xFF,
        temp_raw & 0xFF,
    ])

    updated = bytes(updated)
    validate_schedule(updated)

    if updated == current:
        log.warning("ZWT198 schedule unchanged")
        return

    payload = TuyaData()
    payload.dp_type = TuyaDPType.RAW
    payload.raw = LVBytes(updated)

    dp = TuyaDatapointData(
        dp=109,
        data=payload,
    )

    command = TuyaCommand(
        status=0,
        tsn=device.application.get_sequence(),
        datapoints=[dp],
    )

    # Verify locally before transmission.
    command.serialize()

    if bytes(dp.data.raw) != updated:
        raise ValueError("DP109 RAW payload mismatch")

    log.warning(
        "ZWT198 EDITOR WRITE: %s",
        updated.hex(" ")
    )

    result = await cluster.command(
        cluster.mcu_write_command,
        command,
        expect_reply=False,
        manufacturer=None,
    )

    log.warning(
        "ZWT198 EDITOR command result: %s",
        result,
    )

    # Deliberately do not mark the operation confirmed.
    # Confirmation requires a fresh device report.
    state.set(
        "pyscript.zwt198_editor_status",
        "sent_unconfirmed",
        requested=updated.hex(),
    )
    # Update graph with the requested schedule.
    update_schedule_chart(updated)
    

@state_trigger("input_select.zwt198_programhely")
async def zwt198_programhely_changed(value=None, old_value=None):

    # Az előző, még várakozó betöltést érvénytelenítjük.
    task.unique("zwt198_auto_load")

    # Gyors lépkedésnél csak az utolsó kiválasztást töltjük be.
    await task.sleep(0.3)

    if value not in SLOTS:
        return

    if hass.states.get(
        "pyscript.zwt198_editor_status"
    ).state == "writing":
        log.warning("ZWT198: write in progress, load skipped")
        return

    await hass.services.async_call(
        "pyscript",
        "zwt198_schedule_load",
        {},
        blocking=True,
    )

