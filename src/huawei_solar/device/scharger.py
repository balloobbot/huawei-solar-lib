"""Huawei SCharger device support."""

from __future__ import annotations

from huawei_solar import register_names as rn

from .base import HuaweiSolarDevice


class SChargerDevice(HuaweiSolarDevice):
    """An SCharger device."""

    software_version: str

    @classmethod
    def supports_device(cls, model_name: str) -> bool:
        """Check if this class support the given device."""
        return model_name.startswith("FusionCharge")

    async def _populate_additional_fields(self) -> None:
        identity = await self.get_multiple([rn.CHARGER_ESN, rn.CHARGER_SOFTWARE_VERSION])
        self.serial_number = identity[rn.CHARGER_ESN]
        self.software_version = identity[rn.CHARGER_SOFTWARE_VERSION]

        self.model_name = await self.get(rn.CHARGER_MODEL)
