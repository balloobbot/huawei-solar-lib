"""Pytest configuration and fixtures for huawei-solar tests."""

from __future__ import annotations

import pytest
from huawei_solar.register_values import StorageProductModel
from modbus_connection.mock import MockModbusConnection, MockModbusUnit

from huawei_solar.device import SUN2000Device

# Registers as a real SUN2000-3KTL-L1 reports them, keyed by start address.
# Loaded into the mock's holding-register store, so a component reads whichever
# block its plan asks for rather than the exact requests the old table made.
MOCK_HOLDING_REGISTERS: dict[int, list[int]] = {
    30000: [21333, 20018, 12336, 12333, 13131, 21580, 11596, 12544, 0, 0, 0, 0, 0, 0, 0],
    30015: [18518, 13104, 12849, 13874, 12592, 14389, 0, 0, 0, 0],
    30070: [348],
    30071: [2],
    30072: [2],
    30073: [0, 3000],
    30075: [0, 3300],
    30077: [0, 3300],
    30079: [0, 1980],
    30081: [65535, 63556],
    32000: [1],
    32002: [0],
    32003: [0, 0],
    32008: [257],
    32009: [514],
    32010: [27],
    32016: [0, 0, 0, 0, 0, 0, 0, 0],
    32064: [0, 0, 0, 0, 0],
    32069: [0],
    32070: [0],
    32071: [0],
    32072: [0, 0],
    32074: [0, 0],
    32076: [0, 0],
    32078: [0, 225],
    32080: [0, 0],
    32082: [0, 0],
    32084: [0],
    32085: [0],
    32086: [0],
    32087: [0],
    32088: [3000],
    32089: [40960],
    32090: [0],
    32091: [25069, 6645],
    32093: [25069, 35661],
    32106: [0, 20734],
    32114: [0, 65],
    37200: [10],
    37201: [0],
    40000: [25069, 53611],
    42000: [18],
    43006: [60],
}


@pytest.fixture
def huawei_unit() -> MockModbusUnit:
    """Return a mock Modbus unit preloaded with a SUN2000's register contents."""
    connection = MockModbusConnection()
    unit = connection.for_unit(1)
    unit.holding.update(MOCK_HOLDING_REGISTERS)
    return unit


@pytest.fixture
def sun2000_device(huawei_unit: MockModbusUnit) -> SUN2000Device:
    """Return a SUN2000 device reading from the mock unit."""
    device = SUN2000Device(huawei_unit, model_name="SUN2000-9KTL-123", primary_device=None)

    device._time_zone = 60
    device.battery_1_type = StorageProductModel.HUAWEI_LUNA2000

    return device
