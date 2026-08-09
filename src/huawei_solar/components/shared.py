"""Registers every Huawei device answers, whatever its type."""

from __future__ import annotations

from huawei_solar.components.base import HuaweiComponent
from huawei_solar.fields import (
    i16,
    text,
    u16,
)


class DeviceIdentity(HuaweiComponent):
    """Identity and clock registers common to every device type."""

    model_name = text(30000, 15)
    serial_number = text(30015, 10)
    software_version = text(30050, 15)
    daylight_saving_time = u16(42900, convert=bool, writable=True)
    time_zone = i16(43006, unit="min", writable=True)
