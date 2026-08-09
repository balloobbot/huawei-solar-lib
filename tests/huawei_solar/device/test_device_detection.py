"""Tests for device detection in huawei_solar.device.__init__.

These drive a real in-memory Modbus unit rather than a stubbed client, so the
probe chain is exercised the way it runs against a device: a register the device
does not serve answers with a Modbus exception, and detection falls through to
the next probe.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest
from huawei_solar.device.emma import EMMADevice
from huawei_solar.device.meter import MeterDevice
from huawei_solar.device.scharger import SChargerDevice
from huawei_solar.device.sdongle import SDongleDevice
from huawei_solar.device.smartlogger import SmartLoggerDevice
from huawei_solar.device.sun2000 import SUN2000Device
from huawei_solar.exceptions import DeviceDetectionError, ReadException
from huawei_solar.registry import REGISTER_LOCATIONS
from modbus_connection import IllegalDataAddressError, IllegalDataValueError, ServerDeviceFailureError
from modbus_connection.mock import MockModbusConnection, MockModbusUnit

from huawei_solar import register_names as rn
from huawei_solar.device import DEFAULT_SDONGLE_UNIT_ID, detect_device_type, get_device_class_for_model

if TYPE_CHECKING:
    from collections.abc import Iterable

ILLEGAL_DATA_ADDRESS = 0x02
ILLEGAL_DATA_VALUE = 0x03

# Every register the probe chain can reach for, in the order it tries them.
PROBE_REGISTERS = (
    rn.SDONGLE_DEVICE_SEARCH_STATUS,
    rn.MODEL_NAME,
    rn.SMARTLOGGER_EQUIPMENT_SERIAL_NUMBER_ESN,
    rn.SMARTLOGGER_DEVICE_NAME,
    rn.SMARTLOGGER_EXTERNAL_METER_ACTIVE_POWER,
)


def _span(name: str) -> range:
    location = REGISTER_LOCATIONS[name]
    field = location.definition()
    start = field.address + field.stride * ((location.instance or 1) - 1)
    return range(start, start + field.count)


def _unit(
    answers: dict[str, Any] | None = None,
    *,
    absent: Iterable[str] = PROBE_REGISTERS,
    error: Exception | None = None,
) -> MockModbusUnit:
    """Build a mock unit that answers ``answers`` and refuses everything in ``absent``."""
    unit = MockModbusConnection().for_unit(1)
    answers = answers or {}
    for name in absent:
        if name in answers:
            continue
        for address in _span(name):
            unit.fail_read(address, error or IllegalDataAddressError())
    for name, value in answers.items():
        words = REGISTER_LOCATIONS[name].definition().encode(value)
        for offset, word in enumerate(words):
            unit.holding[_span(name).start + offset] = word
    return unit


@pytest.fixture
def patched_supports_device(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(SUN2000Device, "supports_device", staticmethod(lambda model: model == "sun2000-model"))
    monkeypatch.setattr(EMMADevice, "supports_device", staticmethod(lambda model: model == "emma-model"))
    monkeypatch.setattr(SChargerDevice, "supports_device", staticmethod(lambda model: model == "scharger-model"))
    monkeypatch.setattr(SDongleDevice, "supports_device", staticmethod(lambda model: model == "sdongle-model"))
    monkeypatch.setattr(
        SmartLoggerDevice,
        "supports_device",
        staticmethod(lambda model: model == "smartlogger-model"),
    )
    monkeypatch.setattr(MeterDevice, "supports_device", staticmethod(lambda model: model == "meter-model"))


@pytest.mark.parametrize(
    ("model_name", "expected_class"),
    [
        ("sun2000-model", SUN2000Device),
        ("emma-model", EMMADevice),
        ("scharger-model", SChargerDevice),
        ("sdongle-model", SDongleDevice),
        ("smartlogger-model", SmartLoggerDevice),
        ("meter-model", MeterDevice),
    ],
)
def test_get_device_class_for_model_all_supported_types(
    patched_supports_device: None,
    model_name: str,
    expected_class: type,
) -> None:
    assert get_device_class_for_model(model_name) is expected_class


def test_get_device_class_for_model_unknown_defaults_to_sun2000(patched_supports_device: None) -> None:
    assert get_device_class_for_model("unknown-model") is SUN2000Device


@pytest.mark.parametrize(
    ("model_name", "expected_class"),
    [
        ("sun2000-model", SUN2000Device),
        ("emma-model", EMMADevice),
        ("scharger-model", SChargerDevice),
    ],
)
async def test_detect_device_type_from_model_name(
    patched_supports_device: None,
    model_name: str,
    expected_class: type,
) -> None:
    detected_class, detected_name = await detect_device_type(_unit({rn.MODEL_NAME: model_name}), 1)

    assert detected_class is expected_class
    assert detected_name == model_name


@pytest.mark.parametrize("error", [IllegalDataAddressError(), IllegalDataValueError()])
async def test_detect_device_type_smartlogger_when_model_name_unavailable(
    patched_supports_device: None,
    error: Exception,
) -> None:
    """Firmwares differ on which exception code means 'no such register'; both fall through."""
    unit = _unit(
        {
            rn.SMARTLOGGER_EQUIPMENT_SERIAL_NUMBER_ESN: "123456789012",
            rn.SMARTLOGGER_DEVICE_NAME: "smartlogger-model",
        },
        error=error,
    )

    detected_class, detected_name = await detect_device_type(unit, 1)

    assert detected_class is SmartLoggerDevice
    assert detected_name == "smartlogger-model"


async def test_detect_device_type_propagates_unrelated_read_exception(
    patched_supports_device: None,
) -> None:
    """Modbus exception codes other than 0x02/0x03 must propagate, not be swallowed."""
    unit = _unit(absent=[rn.MODEL_NAME], error=ServerDeviceFailureError())

    with pytest.raises(ReadException):
        await detect_device_type(unit, 1)


async def test_detect_device_type_sdongle_fast_track_on_unit_100() -> None:
    unit = _unit({rn.SDONGLE_DEVICE_SEARCH_STATUS: 1})

    detected_class, detected_name = await detect_device_type(unit, DEFAULT_SDONGLE_UNIT_ID)

    assert detected_class is SDongleDevice
    assert detected_name == "SDongle"


async def test_detect_device_type_smartlogger_via_esn_fallback() -> None:
    """Firmwares with neither MODEL_NAME nor SMARTLOGGER_DEVICE_NAME still expose the ESN."""
    unit = _unit({rn.SMARTLOGGER_EQUIPMENT_SERIAL_NUMBER_ESN: "102120056473"})

    detected_class, detected_name = await detect_device_type(unit, 7)

    assert detected_class is SmartLoggerDevice
    assert detected_name == "SmartLogger"


async def test_detect_device_type_meter_via_active_power_probe() -> None:
    """Power meters expose neither MODEL_NAME nor SMARTLOGGER_DEVICE_NAME, but answer 32278."""
    unit = _unit({rn.SMARTLOGGER_EXTERNAL_METER_ACTIVE_POWER: -1394})

    detected_class, detected_name = await detect_device_type(unit, 11)

    assert detected_class is MeterDevice
    assert detected_name == "PowerMeter"


async def test_detect_device_type_sdongle_fallback_when_other_registers_illegal() -> None:
    unit = _unit({rn.SDONGLE_DEVICE_SEARCH_STATUS: 1})

    detected_class, detected_name = await detect_device_type(unit, 1)

    assert detected_class is SDongleDevice
    assert detected_name == "SDongle"


async def test_detect_device_type_raises_when_no_detection_path_matches() -> None:
    unit = _unit()

    with pytest.raises(DeviceDetectionError, match="Unable to detect the device type"):
        await detect_device_type(unit, 1)
