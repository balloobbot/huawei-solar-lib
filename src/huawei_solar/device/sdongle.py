"""Huawei SDongle device support."""

from __future__ import annotations

from huawei_solar import register_names as rn

from .base import HuaweiSolarDevice


class SDongleDevice(HuaweiSolarDevice):
    """An SDongle device."""

    @classmethod
    def supports_device(cls, model_name: str) -> bool:
        """Check if this class support the given device."""
        return model_name.startswith("SDongle")

    async def _populate_additional_fields(self) -> None:
        identity = await self.get_multiple([rn.MODEL_NAME, rn.SERIAL_NUMBER])
        self.model_name = identity[rn.MODEL_NAME]
        self.serial_number = identity[rn.SERIAL_NUMBER]
