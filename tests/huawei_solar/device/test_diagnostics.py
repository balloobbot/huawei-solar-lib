"""The raw register dump an issue report carries.

It is read fresh from the device and returned undecoded, keyed by address space
and absolute address. What matters is what it covers: the registers read once
at setup identify the device, and no poll ever goes back to them.
"""

from __future__ import annotations

import huawei_solar.register_names as rn
import pytest
from huawei_solar.exceptions import ConnectionInterruptedException
from modbus_connection import ModbusConnectionError, ModbusTimeoutError
from modbus_connection.mock import MockModbusUnit

from huawei_solar.device import SUN2000Device

INVERTER_BLOCK = 32064  # input_power
METER_BLOCK = 37132  # active_grid_A_power
SERIAL_NUMBER_BLOCK = 30015  # read once, while setting the device up


async def test_the_dump_covers_the_registers_only_setup_reads(huawei_unit: MockModbusUnit) -> None:
    device = await SUN2000Device.create(huawei_unit, model_name="SUN2000-9KTL-123")

    holding = (await device.async_read_raw())["holding"]

    assert SERIAL_NUMBER_BLOCK in holding
    assert INVERTER_BLOCK not in holding  # nothing has polled it yet


async def test_the_dump_grows_with_what_a_poll_reads(huawei_unit: MockModbusUnit) -> None:
    device = await SUN2000Device.create(huawei_unit, model_name="SUN2000-9KTL-123")
    await device.batch_update([rn.INPUT_POWER])

    holding = (await device.async_read_raw())["holding"]

    assert INVERTER_BLOCK in holding
    assert SERIAL_NUMBER_BLOCK in holding


async def test_a_component_that_will_not_answer_is_left_out(huawei_unit: MockModbusUnit) -> None:
    """All-or-nothing would lose the whole map to the one component at issue."""
    device = await SUN2000Device.create(huawei_unit, model_name="SUN2000-9KTL-123")
    await device.batch_update([rn.INPUT_POWER])
    huawei_unit.fail_read(INVERTER_BLOCK, ModbusTimeoutError("slow inverter block"))

    holding = (await device.async_read_raw())["holding"]

    assert INVERTER_BLOCK not in holding
    assert SERIAL_NUMBER_BLOCK in holding


async def test_a_dead_link_raises_rather_than_returning_half_a_dump(huawei_unit: MockModbusUnit) -> None:
    device = await SUN2000Device.create(huawei_unit, model_name="SUN2000-9KTL-123")
    huawei_unit.fail_requests(ModbusConnectionError("link down"))

    with pytest.raises(ConnectionInterruptedException):
        await device.async_read_raw()


async def test_an_offline_power_meter_is_not_poked_by_the_dump(huawei_unit: MockModbusUnit) -> None:
    """Reading the meter while it is offline makes the inverter drop the connection.

    The dump goes through the poll's own filter, so it cannot be the one thing
    that does it.
    """
    device = await SUN2000Device.create(huawei_unit, model_name="SUN2000-9KTL-123")
    device.power_meter_online = True
    await device.batch_update([rn.ACTIVE_GRID_A_POWER])

    device.power_meter_online = False  # as a power outage leaves it
    huawei_unit.read_events.clear()
    holding = (await device.async_read_raw())["holding"]

    assert METER_BLOCK not in holding
    assert all(event.address != METER_BLOCK for event in huawei_unit.read_events)
    assert SERIAL_NUMBER_BLOCK in holding
