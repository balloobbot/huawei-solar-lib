"""Tests for the SUN2000Device class."""

from __future__ import annotations

import huawei_solar.register_names as rn
import pytest
from huawei_solar.components import sun2000 as components
from huawei_solar.exceptions import ReadException
from huawei_solar.registry import REGISTER_LOCATIONS
from modbus_connection import IllegalDataAddressError
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


async def test_restricting_to_one_alias_still_plans_its_read(huawei_unit: MockModbusUnit) -> None:
    """A component narrowed to an aliased register can still be read.

    Narrowing marks the dropped alias's address unreadable, which would leave
    the twin that is still wanted outside every readable range. HuaweiComponent
    clears the narrowed map, so the planner keeps the register.
    """
    component = components.Inverter(huawei_unit)
    component.restrict_fields(["grid_voltage"])
    await component.async_update()

    assert [(event.address, event.count) for event in huawei_unit.read_events] == [(32066, 1)]


async def _refuse_block_while_polling_both(
    device: SUN2000Device,
    unit: MockModbusUnit,
    refused_block: int,
) -> None:
    """Poll an inverter and a power-meter register with one of the blocks refused."""
    device.power_meter_online = True
    unit.fail_read(refused_block, IllegalDataAddressError())

    with pytest.raises(ReadException):
        await device.batch_update([rn.INPUT_POWER, rn.ACTIVE_GRID_A_POWER])


async def test_a_refused_meter_block_marks_the_meter_offline(
    sun2000_device: SUN2000Device,
    huawei_unit: MockModbusUnit,
) -> None:
    """The refused block names the power-meter register, so the meter is blamed."""
    await _refuse_block_while_polling_both(sun2000_device, huawei_unit, 37132)

    assert sun2000_device.power_meter_online is False


async def test_a_refused_inverter_block_leaves_the_meter_alone(
    sun2000_device: SUN2000Device,
    huawei_unit: MockModbusUnit,
) -> None:
    """The refused block covered only the inverter register, so the meter is not blamed.

    The two registers are read as separate blocks, and a refusal names the
    block it was refused, so the poll's other registers keep their standing.
    """
    await _refuse_block_while_polling_both(sun2000_device, huawei_unit, 32064)

    assert sun2000_device.power_meter_online is True
