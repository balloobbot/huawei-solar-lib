"""Definitions of the devices supported by this library."""

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, Any

from modbus_connection import ExceptionCode

from huawei_solar import register_names as rn
from huawei_solar.exceptions import DeviceDetectionError, ReadException

from .base import HuaweiSolarDevice, HuaweiSolarDeviceWithLogin
from .emma import EMMADevice
from .meter import MeterDevice
from .scharger import SChargerDevice
from .sdongle import SDongleDevice
from .smartlogger import SmartLoggerDevice
from .sun2000 import SUN2000Device

if TYPE_CHECKING:
    from modbus_connection import ModbusUnit

_LOGGER = getLogger(__name__)

DEFAULT_SDONGLE_UNIT_ID = 100

# Different firmwares answer with one or the other for the same "this register
# is not here" condition, so probing has to treat both as "try the next probe".
_ABSENT_CODES = {ExceptionCode.ILLEGAL_DATA_VALUE, ExceptionCode.ILLEGAL_DATA_ADDRESS}


class _Probe(HuaweiSolarDevice):
    """A device of not-yet-known type, used only to read identifying registers."""

    @classmethod
    def supports_device(cls, model_name: str) -> bool:  # noqa: ARG003
        """Never chosen by detection; this class only exists to read registers."""
        return False

    async def _populate_additional_fields(self) -> None:
        """Nothing to populate: a probe is thrown away once the type is known."""


async def _try_read_register(unit: ModbusUnit, register: str) -> Any | None:  # noqa: ANN401
    """Read a register, returning ``None`` if the device reports it as inaccessible.

    Re-raises any other modbus or transport error so genuine failures still surface.
    """
    try:
        return await _Probe(unit, "probe").get(register)
    except ReadException as err:
        if err.modbus_exception_code in _ABSENT_CODES:
            return None

        # re-raise any other exception that occurred
        raise


def get_device_class_for_model(model_name: str) -> type[HuaweiSolarDevice]:
    """Get the device class for the given model name."""
    for candidate_class in [
        SUN2000Device,
        EMMADevice,
        SChargerDevice,
        SDongleDevice,
        SmartLoggerDevice,
        MeterDevice,
    ]:
        if candidate_class.supports_device(model_name):
            return candidate_class

    _LOGGER.warning("Unknown product model '%s'. Defaulting to a SUN2000 device.", model_name)

    # Default to SUN2000Device if no specific match is found
    return SUN2000Device


async def detect_device_type(unit: ModbusUnit, unit_id: int) -> tuple[type[HuaweiSolarDevice], str]:
    """Detect the type of the device answering on ``unit``."""

    async def _detect_sdongle() -> bool:
        device_search_status = await _try_read_register(unit, rn.SDONGLE_DEVICE_SEARCH_STATUS)
        if device_search_status is None:
            _LOGGER.warning("Failed to detect device type for unit ID %d.", unit_id)
            return False
        _LOGGER.debug(
            "Successfully retrieved SDongle 'device search status' register for unit ID %d: %s",
            unit_id,
            device_search_status,
        )
        return True

    # Unit ID 100 is typically used by an SDongle. Fast track checking for that.
    if unit_id == DEFAULT_SDONGLE_UNIT_ID and await _detect_sdongle():
        return SDongleDevice, "SDongle"

    model_name = await _try_read_register(unit, rn.MODEL_NAME)
    if model_name is not None:
        return get_device_class_for_model(model_name), model_name
    _LOGGER.info("MODEL_NAME is an illegal data address for unit ID %d.", unit_id)

    # The SmartLogger does not have a MODEL_NAME register, so we need to detect it differently.
    #
    # Some SmartLogger firmwares (e.g. SmartLogger3000A) expose neither MODEL_NAME nor
    # SMARTLOGGER_DEVICE_NAME, but still respond to the equipment serial number register.
    # A successful read there is a strong enough signal to identify the device as a
    # SmartLogger; SmartLoggerDevice.supports_device() accepts any name that starts
    # with "SmartLogger", so the generic model string keeps the contract.
    if (await _try_read_register(unit, rn.SMARTLOGGER_EQUIPMENT_SERIAL_NUMBER_ESN)) is not None:
        _LOGGER.info("Detected SmartLogger via ESN register for unit ID %d.", unit_id)

        # fallback for when SMARTLOGGER_DEVICE_NAME is not available
        smartlogger_device_name = (await _try_read_register(unit, rn.SMARTLOGGER_DEVICE_NAME)) or "SmartLogger"

        return SmartLoggerDevice, smartlogger_device_name
    _LOGGER.info("SMARTLOGGER_EQUIPMENT_SERIAL_NUMBER_ESN unavailable for unit ID %d.", unit_id)

    # Power meters connected to a SmartLogger do not expose any of the identifying
    # registers above, but they do answer the meter-telemetry block (see Huawei
    # SmartLogger ModBus Interface Definitions, Issue 35, Table 2-5). Active power
    # at register 32278 is a reliable probe: SUN2000 inverters do not define it,
    # and the SmartLogger itself does not aggregate meter data at its own slave.
    if await _try_read_register(unit, rn.SMARTLOGGER_EXTERNAL_METER_ACTIVE_POWER) is not None:
        _LOGGER.info("Detected power meter via meter telemetry probe for unit ID %d.", unit_id)
        return MeterDevice, "PowerMeter"
    _LOGGER.info("Meter telemetry probe unavailable for unit ID %d.", unit_id)

    if await _detect_sdongle():
        return SDongleDevice, "SDongle"

    # If we reach here, we couldn't detect the device type
    _LOGGER.warning("Failed to detect device type.")
    msg = "Unable to detect the device type. The device may not be supported or may not be responding correctly."
    raise DeviceDetectionError(msg)


async def create_device_instance(unit: ModbusUnit, unit_id: int) -> HuaweiSolarDevice:
    """Detect the connected device and create the appropriate instance."""
    device_type, model_name = await detect_device_type(unit, unit_id)
    return await device_type.create(
        unit,
        model_name=model_name,
        primary_device=None,  # we are creating the primary device!
    )


async def create_sub_device_instance(
    primary_device: HuaweiSolarDevice,
    connection: Any,  # noqa: ANN401
    unit_id: int,
) -> HuaweiSolarDevice:
    """Create a device for another unit id reachable over the same connection."""
    sub_unit = connection.for_unit(unit_id)
    device_type, model_name = await detect_device_type(sub_unit, unit_id)
    return await device_type.create(
        sub_unit,
        model_name=model_name,
        primary_device=primary_device,
    )


__all__ = [
    "EMMADevice",
    "HuaweiSolarDevice",
    "HuaweiSolarDeviceWithLogin",
    "MeterDevice",
    "SChargerDevice",
    "SDongleDevice",
    "SUN2000Device",
    "SmartLoggerDevice",
    "create_device_instance",
    "create_sub_device_instance",
    "detect_device_type",
]
