"""The register map of an SCharger EV charger."""

from __future__ import annotations

from huawei_solar.components.base import HuaweiComponent
from huawei_solar.fields import (
    i32,
    text,
    u32,
)


class SCharger(HuaweiComponent):
    """SCharger status and energy counters."""

    serial_number = text(30015, 16)
    software_version = text(30031, 16)
    rated_power = u32(30076, unit="kW", gain=10)
    model = text(30078, 14)
    phase_a_voltage = u32(30500, unit="V", gain=10)
    phase_b_voltage = u32(30502, unit="V", gain=10)
    phase_c_voltage = u32(30504, unit="V", gain=10)
    total_energy_charged = u32(30506, unit="kWh", gain=1000)
    temperature = i32(30508, unit="°C", gain=10)
