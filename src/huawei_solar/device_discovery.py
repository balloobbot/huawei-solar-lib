"""Device discovery for Huawei inverters."""

import logging
import struct
from dataclasses import dataclass
from typing import Literal

from modbus_connection import ModbusUnit

from huawei_solar import session

_LOGGER = logging.getLogger(__name__)


DEVICE_INFOS_START_OBJECT_ID = 0x87


@dataclass(frozen=True, slots=True)
class DeviceInfo:
    """Device information."""

    model: str | None
    software_version: str | None
    interface_protocol_version: str | None
    esn: str | None
    device_id: int | None
    feature_version: str | None
    unknown_field: str | None
    product_type: str | None


@dataclass(frozen=True, slots=True)
class DeviceIdentifier:
    """Device identifier information."""

    vendor: str
    product_code: str
    main_revision_version: str
    other_data: dict[int, bytes]


async def get_device_identifiers(unit: ModbusUnit) -> DeviceIdentifier:
    """Read the device identifiers from the inverter."""
    objects = await _read_device_identifier_objects(unit, 0x01, 0x00)

    return DeviceIdentifier(
        vendor=objects.pop(0x00).decode("ascii"),
        product_code=objects.pop(0x01).decode("ascii"),
        main_revision_version=objects.pop(0x02).decode("ascii"),
        other_data=objects,
    )


async def get_device_infos(unit: ModbusUnit) -> list[DeviceInfo]:
    """Read the device infos from the inverter."""
    objects = await _read_device_identifier_objects(unit, 0x03, DEVICE_INFOS_START_OBJECT_ID)

    def _parse_device_entry(device_info_str: str) -> DeviceInfo:
        raw_device_info: dict[int, str] = {}
        for entry in device_info_str.split(";"):
            key, value = entry.split("=")
            raw_device_info[int(key)] = value

        return DeviceInfo(
            model=raw_device_info.get(1),
            software_version=raw_device_info.get(2),
            interface_protocol_version=raw_device_info.get(3),
            esn=raw_device_info.get(4),
            device_id=int(raw_device_info[5]) if 5 in raw_device_info else None,  # noqa: PLR2004
            feature_version=raw_device_info.get(6),
            unknown_field=raw_device_info.get(7),
            product_type=raw_device_info.get(8),
        )

    if DEVICE_INFOS_START_OBJECT_ID in objects:
        (number_of_devices,) = struct.unpack(">B", objects.pop(DEVICE_INFOS_START_OBJECT_ID))
    else:
        _LOGGER.warning("No 0x87 entry with number of devices found in objects. Ignoring")
        number_of_devices = -1

    device_infos = [_parse_device_entry(device_info_bytes.decode("ascii")) for device_info_bytes in objects.values()]

    if number_of_devices >= 0 and len(device_infos) != number_of_devices:
        _LOGGER.warning(
            "Number of device infos does not match the number of devices: %d != %d",
            len(device_infos),
            number_of_devices,
        )

    return device_infos


async def _read_device_identifier_objects(
    unit: ModbusUnit,
    read_dev_id_code: Literal[0x01, 0x03],
    object_id: int,
) -> dict[int, bytes]:
    """Read all the objects of a certain ReadDevId code."""
    return await session.read_device_identification(unit, read_dev_id_code, object_id)
