"""Huawei EMMA (SmartHEMS) device support."""

from __future__ import annotations

from huawei_solar import register_names as rn

from .base import HuaweiSolarDevice


class EMMADevice(HuaweiSolarDevice):
    """A Huawei EMMA device.

    Also called 'SmartHEMS' by Huawei.
    """

    software_version: str

    @classmethod
    def supports_device(cls, model_name: str) -> bool:
        """Check if this class support the given device."""
        return model_name.startswith("SmartHEMS")

    async def has_write_permission(self) -> bool:
        """EMMA always gives write access."""
        return True

    async def _populate_additional_fields(self) -> None:
        identity = await self.get_multiple([rn.SERIAL_NUMBER, rn.SOFTWARE_VERSION])
        self.serial_number = identity[rn.SERIAL_NUMBER]
        self.software_version = identity[rn.SOFTWARE_VERSION]

        self.model_name = await self.get(rn.EMMA_MODEL)
