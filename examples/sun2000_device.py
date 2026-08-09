"""Read a SUN2000 inverter over a shared Modbus connection."""

import asyncio
import logging

from huawei_solar import (
    SUN2000Device,
    create_device_instance,
    create_sub_device_instance,
    create_tcp_connection,
    get_device_identifiers,
    get_device_infos,
)
from huawei_solar import register_names as rn

logging.basicConfig(level=logging.DEBUG)

PRIMARY_UNIT_ID = 0


async def main() -> None:
    """Read an inverter, and anything else answering on the same link."""
    # One connection carries every device: the inverter answers on its own unit
    # id, batteries and meters behind it on theirs. It connects on the first
    # request, so nothing needs to be opened up front.
    connection = create_tcp_connection(host="192.168.1.1", port=503)
    try:
        unit = connection.for_unit(PRIMARY_UNIT_ID)

        print(await get_device_identifiers(unit))
        print(await get_device_infos(unit))

        device = await create_device_instance(unit, PRIMARY_UNIT_ID)
        assert isinstance(device, SUN2000Device)

        # Writing, and reading the optimizer files, both need a login session.
        await device.login("installer", "00000a")

        print(
            await device.batch_update(
                [
                    rn.ACTIVE_POWER_FIXED_VALUE_DERATING,
                    rn.ACTIVE_POWER_PERCENTAGE_DERATING,
                    rn.STORAGE_CAPACITY_CONTROL_MODE,
                    rn.STORAGE_CAPACITY_CONTROL_SOC_PEAK_SHAVING,
                    rn.STORAGE_CAPACITY_CONTROL_PERIODS,
                ],
            ),
        )

        print(await device.get_optimizer_system_information_data())
        print(await device.get_latest_optimizer_history_data())

        # A sub-device shares the same connection rather than opening its own.
        battery = await create_sub_device_instance(device, connection, unit_id=1)
        print(battery.model_name, battery.serial_number)

        await device.stop()
    finally:
        await connection.close()


asyncio.run(main())
