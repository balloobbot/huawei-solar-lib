#!/usr/bin/env python3

"""Query a Huawei Solar device and print every value.

Detects what is answering, reads it once and dumps it to the terminal — the
quickest way to check a real installation with no application around it.

::

    uv run script/query.py 192.168.1.1
    uv run script/query.py /dev/ttyUSB0 --transport serial --unit 1

Every component is a read of its own, so a full inverter with batteries costs
tens of round-trips; behind an SDongle, which answers slowly, that takes a
while. The read count at the end says what it cost.
"""

from __future__ import annotations

import argparse
import asyncio
from typing import TYPE_CHECKING

from huawei_solar import (
    EMMADevice,
    HuaweiSolarDevice,
    HuaweiSolarException,
    MeterDevice,
    SChargerDevice,
    SDongleDevice,
    SmartLoggerDevice,
    SUN2000Device,
    create_device_instance,
)
from huawei_solar import register_values as rv
from huawei_solar.components import emma, scharger, sdongle, shared, smartlogger, sun2000
from huawei_solar.connection import DEFAULT_MESSAGE_SPACING, DEFAULT_UNIT_ID
from modbus_connection import ModbusError
from modbus_connection.cli_helper import (
    CountingUnit,
    add_connection_args,
    connect_from_args,
    print_component,
)

if TYPE_CHECKING:
    from huawei_solar.components.base import HuaweiComponent

# Huawei devices are reached over the network — an SDongle, an EMMA, or the
# inverter's own WiFi-AP — or over the RS485A1/B1 pins on the COM port. Each
# transport keeps its default framing: MBAP on TCP, RTU on the serial line.
CONNECTIONS: tuple[tuple[str, str | None], ...] = (("tcp", None), ("serial", None))

# The components each model answers for. The register table spans the whole
# fleet, so a dump has to be narrowed to the model detected on the line. The
# write-only ``Commands`` components are left out: the device refuses to read
# them back.
COMPONENTS: dict[type[HuaweiSolarDevice], tuple[type[HuaweiComponent], ...]] = {
    SUN2000Device: (
        shared.DeviceIdentity,
        sun2000.ProductInfo,
        sun2000.Inverter,
        sun2000.PVString,
        sun2000.Diagnostics,
        sun2000.StorageUnit,
        sun2000.StorageUnit1Only,
        sun2000.StorageSettings,
        sun2000.PowerMeter,
        sun2000.Optimizers,
        sun2000.BatteryPack,
        sun2000.Configuration,
    ),
    EMMADevice: (
        shared.DeviceIdentity,
        emma.Emma,
        emma.EmmaExternalMeter,
        emma.EmmaBuiltInMeter,
        emma.EmmaSettings,
    ),
    SChargerDevice: (shared.DeviceIdentity, scharger.SCharger),
    SDongleDevice: (shared.DeviceIdentity, sdongle.SDongle),
    SmartLoggerDevice: (
        smartlogger.SmartLogger,
        smartlogger.SmartLoggerAlarms,
        smartlogger.SmartLoggerExternalMeter,
    ),
    # A meter behind a SmartLogger answers only the meter telemetry block.
    MeterDevice: (smartlogger.SmartLoggerExternalMeter,),
}

# The components that exist once per string, storage unit or battery pack.
REPEATED = (sun2000.PVString, sun2000.StorageUnit, sun2000.BatteryPack)


def instances(device: HuaweiSolarDevice, component: type[HuaweiComponent]) -> tuple[int, ...]:
    """Which instances of ``component`` this installation has; empty if none.

    Setup settled what is fitted, so a dump asks only for hardware that is
    there rather than walking every string and pack the map allows.
    """
    if not isinstance(device, SUN2000Device):
        return (1,)
    if component is sun2000.PVString:
        return tuple(range(1, device.pv_string_count + 1))
    batteries = (device.battery_1_type, device.battery_2_type)
    if component is sun2000.StorageUnit:
        return tuple(i for i in (1, 2) if batteries[i - 1] != rv.StorageProductModel.NONE)
    if component is sun2000.BatteryPack:
        # Three packs per storage unit: 1-3 on the first, 4-6 on the second.
        return tuple(i for i in range(1, 7) if batteries[(i - 1) // 3] != rv.StorageProductModel.NONE)
    has_battery = device.battery_type != rv.StorageProductModel.NONE
    fitted = {
        sun2000.Optimizers: bool(device.has_optimizers),
        sun2000.StorageUnit1Only: has_battery,
        sun2000.StorageSettings: has_battery,
        sun2000.PowerMeter: device.power_meter_online,
    }
    return (1,) if fitted.get(component, True) else ()


def components(device: HuaweiSolarDevice) -> list[tuple[HuaweiComponent, str]]:
    """Every component instance the detected model has, in the order it is polled."""
    built = [
        (
            component_class(device.unit, index),
            f"{component_class.__name__}[{index}]" if component_class in REPEATED else component_class.__name__,
        )
        for component_class in COMPONENTS.get(type(device), ())
        for index in instances(device, component_class)
    ]
    # The library reads low addresses first; a dump follows the same order.
    built.sort(key=lambda item: min(field.address for field in item[0].resolved_fields.values()))
    return built


async def main() -> int:
    """Read one device and print it."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    add_connection_args(parser, connections=CONNECTIONS)
    parser.add_argument("--unit", type=int, default=DEFAULT_UNIT_ID, help="Modbus unit id")
    args = parser.parse_args()

    # Huawei inverters drop frames that arrive back-to-back, so the link is
    # paced the way this library paces its own.
    try:
        connection = await connect_from_args(args, message_spacing=DEFAULT_MESSAGE_SPACING)
    except ModbusError as err:
        print(f"Could not connect: {str(err) or type(err).__name__}")
        return 1

    counting = CountingUnit(connection.for_unit(args.unit))
    try:
        device = await create_device_instance(counting, args.unit)
    except (ModbusError, HuaweiSolarException) as err:
        print(f"Could not reach a device: {str(err) or type(err).__name__}")
        await connection.close()
        return 1

    print(f"{device.model_name} on unit {args.unit}")
    failed: dict[str, ModbusError] = {}
    try:
        for component, title in components(device):
            try:
                await component.async_update()
            except ModbusError as err:
                failed[title] = err
                continue
            print()
            print_component(component, title=title)
    finally:
        await connection.close()

    # A component that will not answer is named rather than printed empty, so a
    # missing block reads as a refusal and not as a device with no values.
    for title, error in failed.items():
        print(f"\n{title}: not read ({str(error) or type(error).__name__})")
    print(f"\n{counting.reads} Modbus reads")
    return 0


raise SystemExit(asyncio.run(main()))
