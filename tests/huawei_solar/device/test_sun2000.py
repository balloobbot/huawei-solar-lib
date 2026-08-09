"""Tests for the SUN2000Device class."""

from __future__ import annotations

import huawei_solar.register_names as rn
from huawei_solar.registry import REGISTER_LOCATIONS
from modbus_connection.mock import MockModbusUnit

from huawei_solar.device import SUN2000Device


async def test_get_model_name(sun2000_device: SUN2000Device) -> None:
    result = await sun2000_device.batch_update([rn.MODEL_NAME])
    assert result == {rn.MODEL_NAME: "SUN2000-3KTL-L1"}


async def test_get_multiple(sun2000_device: SUN2000Device) -> None:
    result = await sun2000_device.batch_update(
        [rn.INPUT_POWER, rn.LINE_VOLTAGE_A_B, rn.LINE_VOLTAGE_B_C, rn.LINE_VOLTAGE_C_A],
    )
    assert result == {
        rn.INPUT_POWER: 0,
        rn.LINE_VOLTAGE_A_B: 0,
        rn.LINE_VOLTAGE_B_C: 0,
        rn.LINE_VOLTAGE_C_A: 0,
    }


async def test_units_come_from_the_field_definitions() -> None:
    """The unit moved onto the field, where the model layer keeps metadata."""
    assert REGISTER_LOCATIONS[rn.INPUT_POWER].definition().unit == "W"
    assert REGISTER_LOCATIONS[rn.LINE_VOLTAGE_A_B].definition().unit == "V"
    assert REGISTER_LOCATIONS[rn.MODEL_NAME].definition().unit is None


async def test_batch_update_pools_neighbouring_registers(
    sun2000_device: SUN2000Device,
    huawei_unit: MockModbusUnit,
) -> None:
    """Registers close together are read as one block, far-apart ones are not.

    input_power (32064, two registers) and line_voltage_A_B (32066) become a
    single three-register read; device_status at 32089 is 23 registers past the
    end of that block, further than the inverter makes it worth reading across.
    """
    await sun2000_device.batch_update(
        [rn.INPUT_POWER, rn.LINE_VOLTAGE_A_B, rn.DEVICE_STATUS, rn.MODEL_NAME, rn.NB_PV_STRINGS],
    )
    assert [(event.address, event.count) for event in huawei_unit.read_events] == [
        (30000, 15),
        (30071, 1),
        (32064, 3),
        (32089, 1),
    ]


async def test_an_aliased_register_does_not_split_its_block(
    sun2000_device: SUN2000Device,
    huawei_unit: MockModbusUnit,
) -> None:
    """Huawei names 32066 twice; reading one alias must not fragment the read.

    grid_voltage and line_voltage_A_B are the same register under the names a
    single-phase and a three-phase inverter use for it.
    """
    await sun2000_device.batch_update([rn.INPUT_POWER, rn.LINE_VOLTAGE_A_B])
    assert [(event.address, event.count) for event in huawei_unit.read_events] == [(32064, 3)]
