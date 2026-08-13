"""One failing component must not take the rest of the poll with it.

A batch update reads its registers component by component. A component that
fails contributes no values - its registers stay out of the result, so only the
entities behind them go unavailable - while every other component still
refreshes. Only a device that answered nothing at all raises.
"""

from __future__ import annotations

import huawei_solar.register_names as rn
import pytest
from huawei_solar.exceptions import ConnectionInterruptedException, ReadException
from modbus_connection import (
    IllegalDataAddressError,
    ModbusConnectionError,
    ModbusTimeoutError,
    ServerDeviceBusyError,
)
from modbus_connection.mock import MockModbusUnit

from huawei_solar.device import SUN2000Device

#: The block each register the tests below poll is read in.
INVERTER_BLOCK = 32064  # input_power
METER_BLOCK = 37132  # active_grid_A_power
METER_STATUS_BLOCK = 37100  # meter_status, read to decide whether to poll the meter
OPTIMIZER_COUNT_BLOCK = 37200  # nb_optimizers, probed once during setup


async def test_a_failed_component_leaves_the_rest_fresh(
    sun2000_device: SUN2000Device,
    huawei_unit: MockModbusUnit,
) -> None:
    sun2000_device.power_meter_online = True
    huawei_unit.fail_read(METER_BLOCK, ModbusTimeoutError("slow meter block"))

    report = await sun2000_device.batch_update_report([rn.INPUT_POWER, rn.ACTIVE_GRID_A_POWER])

    assert not report.complete
    assert set(report.failed) == {"PowerMeter"}
    assert isinstance(report.failed["PowerMeter"], ModbusTimeoutError)
    assert report.updated == {"Inverter"}
    assert report.values == {rn.INPUT_POWER: 0}


async def test_a_failed_component_reports_nothing_rather_than_a_stale_value(
    sun2000_device: SUN2000Device,
    huawei_unit: MockModbusUnit,
) -> None:
    """The component keeps the values it read, but the poll does not hand them out again.

    A value that is one poll old is indistinguishable from a fresh one to the
    caller. Leaving the register out says what actually happened.
    """
    sun2000_device.power_meter_online = True
    first = await sun2000_device.batch_update([rn.INPUT_POWER, rn.ACTIVE_GRID_A_POWER])
    assert first[rn.ACTIVE_GRID_A_POWER] == 0

    huawei_unit.fail_read(METER_BLOCK, ModbusTimeoutError("slow meter block"))
    second = await sun2000_device.batch_update([rn.INPUT_POWER, rn.ACTIVE_GRID_A_POWER])

    assert second == {rn.INPUT_POWER: 0}


async def test_a_dead_link_raises_instead_of_reporting(
    sun2000_device: SUN2000Device,
    huawei_unit: MockModbusUnit,
) -> None:
    huawei_unit.fail_requests(ModbusConnectionError("link down"))

    with pytest.raises(ConnectionInterruptedException):
        await sun2000_device.batch_update([rn.INPUT_POWER, rn.NB_PV_STRINGS])


async def test_a_device_that_answers_nothing_raises(
    sun2000_device: SUN2000Device,
    huawei_unit: MockModbusUnit,
) -> None:
    """A poll in which nothing came back is a device that is gone, and goes out as one.

    Home Assistant's coordinator drops the Modbus link after a few timed-out
    updates in a row, which an empty report would never trigger.
    """
    huawei_unit.fail_requests(ModbusTimeoutError("no answer"))

    with pytest.raises(TimeoutError):
        await sun2000_device.batch_update([rn.INPUT_POWER, rn.NB_PV_STRINGS])


async def test_reading_one_register_still_raises(
    sun2000_device: SUN2000Device,
    huawei_unit: MockModbusUnit,
) -> None:
    """Nothing is contained when the poll is a single register: get() still raises.

    The setup probes are built on it and read the answer from the exception.
    """
    huawei_unit.fail_read(INVERTER_BLOCK, IllegalDataAddressError())

    with pytest.raises(ReadException):
        await sun2000_device.get(rn.INPUT_POWER)


async def test_reading_several_registers_raises_rather_than_answering_partly(
    sun2000_device: SUN2000Device,
    huawei_unit: MockModbusUnit,
) -> None:
    """get_multiple() is asked for values, not for a poll: a missing one is an error.

    Setup reads its identity this way, across two components.
    """
    huawei_unit.fail_read(INVERTER_BLOCK, IllegalDataAddressError())

    with pytest.raises(ReadException):
        await sun2000_device.get_multiple([rn.INPUT_POWER, rn.MODEL_NAME])


async def test_every_component_refreshes_on_a_healthy_device(
    sun2000_device: SUN2000Device,
) -> None:
    report = await sun2000_device.batch_update_report([rn.INPUT_POWER, rn.NB_PV_STRINGS, rn.MODEL_NAME])

    assert report.complete
    assert report.failed == {}
    assert report.updated == {"Inverter", "ProductInfo", "DeviceIdentity"}


async def test_a_failed_meter_status_probe_does_not_take_the_poll_down(
    sun2000_device: SUN2000Device,
    huawei_unit: MockModbusUnit,
) -> None:
    """The probe that shapes the poll runs ahead of it, so its failure is contained too."""
    assert sun2000_device.power_meter_online is False  # so the probe runs
    huawei_unit.fail_read(METER_STATUS_BLOCK, ModbusTimeoutError("slow meter"))

    result = await sun2000_device.batch_update([rn.INPUT_POWER, rn.ACTIVE_GRID_A_POWER])

    assert result == {rn.INPUT_POWER: 0}


async def test_a_refused_setup_probe_leaves_the_sub_system_absent(huawei_unit: MockModbusUnit) -> None:
    huawei_unit.fail_read(OPTIMIZER_COUNT_BLOCK, IllegalDataAddressError())

    device = await SUN2000Device.create(huawei_unit, model_name="SUN2000-9KTL-123")

    assert device.has_optimizers is False


async def test_a_transient_setup_failure_is_not_taken_for_absence(huawei_unit: MockModbusUnit) -> None:
    """A busy device must not have its optimizers written off until it is reloaded.

    Setup fails instead, leaving no device object to carry the wrong answer, so
    the caller sets up again later.
    """
    huawei_unit.fail_read(OPTIMIZER_COUNT_BLOCK, ServerDeviceBusyError())

    with pytest.raises(ReadException):
        await SUN2000Device.create(huawei_unit, model_name="SUN2000-9KTL-123")
