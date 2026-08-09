"""The register map of an EMMA energy-management appliance."""

from __future__ import annotations

from huawei_solar import register_values as rv
from huawei_solar.components.base import HuaweiComponent
from huawei_solar.fields import (
    HuaweiLuna2000TimeOfUseField,
    i16,
    i32,
    i64,
    text,
    u16,
    u32,
    u64,
)


class Emma(HuaweiComponent):
    """Live EMMA telemetry and energy counters."""

    emma_software_version = text(30035, 15)
    emma_model = text(30222, 20)
    inverter_total_absorbed_energy = u64(30302, unit="kWh", gain=100)
    energy_charged_today = u32(30306, unit="kWh", gain=100)
    total_charged_energy = u64(30308, unit="kWh", gain=100)
    energy_discharged_today = u32(30312, unit="kWh", gain=100)
    total_discharged_energy = u64(30314, unit="kWh", gain=100)
    ess_chargeable_energy = u32(30318, unit="kWh", gain=1000)
    ess_dischargeable_energy = u32(30320, unit="kWh", gain=1000)
    rated_ess_capacity = u32(30322, unit="kWh", gain=1000)
    consumption_today = u32(30324, unit="kWh", gain=100)
    total_energy_consumption = u64(30326, unit="kWh", gain=100)
    feed_in_to_grid_today = u32(30330, unit="kWh", gain=100)
    total_feed_in_to_grid = u64(30332, unit="kWh", gain=100)
    supply_from_grid_today = u32(30336, unit="kWh", gain=100)
    total_supply_from_grid = u64(30338, unit="kWh", gain=100)
    inverter_energy_yield_today = u32(30342, unit="kWh", gain=100)
    inverter_total_energy_yield = u32(30344, unit="kWh", gain=100)
    pv_yield_today = u32(30346, unit="kWh", gain=100)
    total_pv_energy_yield = u64(30348, unit="kWh", gain=100)
    pv_output_power = u32(30354, unit="W")
    load_power = u32(30356, unit="W")
    feed_in_power = i32(30358, unit="W")
    battery_charge_discharge_power = i32(30360, unit="W")
    inverter_rated_power = u32(30362, unit="W")
    inverter_active_power = i32(30364, unit="W")
    state_of_capacity = u16(30368, unit="%", gain=100)
    ess_chargeable_capacity = u32(30369, unit="kWh", gain=1000)
    ess_dischargeable_capacity = u32(30371, unit="kWh", gain=1000)
    backup_power_state_of_charge = u16(30373, unit="%", gain=100)
    yield_this_month = u32(30380, unit="kWh", gain=100)
    monthly_energy_consumption = u32(30382, unit="kWh", gain=100)
    monthly_feed_in_to_grid = u32(30384, unit="kWh", gain=100)
    yield_this_year = u32(30386, unit="kWh", gain=100)
    annual_energy_consumption = u32(30388, unit="kWh", gain=100)
    yearly_feed_in_to_grid = u32(30390, unit="kWh", gain=100)
    monthly_supply_from_grid = u32(30394, unit="kWh", gain=100)
    yearly_supply_from_grid = u32(30396, unit="kWh", gain=100)
    backup_time_notification_threshold = u16(30406, unit="min")
    energy_charged_this_month = u32(30407, unit="kWh", gain=100)
    energy_discharged_this_month = u32(30409, unit="kWh", gain=100)
    number_of_inverters_found = u16(30801)
    number_of_chargers_found = u16(30804)
    emma_dst_state = u16(31002)
    emma_local_time = u32(31003, unit="seconds")


class EmmaExternalMeter(HuaweiComponent):
    """The external meter an EMMA reads."""

    emma_external_meter_running_status = u16(30500, convert=rv.EmmaExternalMeterRunningStatus)
    emma_external_meter_phase_a_voltage = u32(30502, unit="V", gain=100)
    emma_external_meter_phase_b_voltage = u32(30504, unit="V", gain=100)
    emma_external_meter_phase_c_voltage = u32(30506, unit="V", gain=100)
    emma_external_meter_line_voltage_a_b = u32(30508, unit="V", gain=100)
    emma_external_meter_line_voltage_b_c = u32(30510, unit="V", gain=100)
    emma_external_meter_line_voltage_c_a = u32(30512, unit="V", gain=100)
    emma_external_meter_phase_a_current = i32(30514, unit="A", gain=10)
    emma_external_meter_phase_b_current = i32(30516, unit="A", gain=10)
    emma_external_meter_phase_c_current = i32(30518, unit="A", gain=10)
    emma_external_meter_active_power = i32(30520, unit="W")
    emma_external_meter_power_factor = i32(30524, gain=1000)
    emma_external_meter_apparent_power = i32(30526, unit="VA")
    emma_external_meter_phase_a_active_power = i32(30528, unit="W")
    emma_external_meter_phase_b_active_power = i32(30530, unit="W")
    emma_external_meter_phase_c_active_power = i32(30532, unit="W")
    emma_external_meter_total_active_energy = i64(30534, unit="kWh", gain=100)
    emma_external_meter_total_negative_active_energy = i64(30542, unit="kWh", gain=100)
    emma_external_meter_total_positive_active_energy = i64(30550, unit="kWh", gain=100)
    phase_a_voltage_external_energy = u32(31895, unit="V", gain=10)
    phase_b_voltage_external_energy = u32(31897, unit="V", gain=10)
    phase_c_voltage_external_energy = u32(31899, unit="V", gain=10)
    line_voltage_a_b_external_energy = u32(31901, unit="V", gain=10)
    line_voltage_b_c_external_energy = u32(31903, unit="V", gain=10)
    line_voltage_c_a_external_energy = u32(31905, unit="V", gain=10)
    phase_a_current_external_energy = i32(31907, unit="A", gain=100)
    phase_b_current_external_energy = i32(31909, unit="A", gain=100)
    phase_c_current_external_energy = i32(31911, unit="A", gain=100)
    active_power_external_energy = i32(31913, unit="W")
    power_factor_external_energy = i32(31917, gain=1000)
    apparent_power_external_energy = i32(31919, unit="VA")
    phase_a_active_power_external_energy = i32(31921, unit="W")
    phase_b_active_power_external_energy = i32(31923, unit="W")
    phase_c_active_power_external_energy = i32(31925, unit="W")
    total_active_energy_external_energy = i64(31927, unit="kWh", gain=100)
    total_negative_active_energy_external_energy = i64(31935, unit="kWh", gain=100)
    total_positive_active_energy_external_energy = i64(31943, unit="kWh", gain=100)


class EmmaBuiltInMeter(HuaweiComponent):
    """The meter built into the EMMA."""

    phase_a_voltage_built_in_energy = u32(31639, unit="V", gain=100)
    phase_b_voltage_built_in_energy = u32(31641, unit="V", gain=100)
    phase_c_voltage_built_in_energy = u32(31643, unit="V", gain=100)
    line_voltage_a_b_built_in_energy = u32(31645, unit="V", gain=100)
    line_voltage_b_c_built_in_energy = u32(31647, unit="V", gain=100)
    line_voltage_c_a_built_in_energy = u32(31649, unit="V", gain=100)
    phase_a_current_built_in_energy = i32(31651, unit="A", gain=10)
    phase_b_current_built_in_energy = i32(31653, unit="A", gain=10)
    phase_c_current_built_in_energy = i32(31655, unit="A", gain=10)
    active_power_built_in_energy = i32(31657, unit="W")
    power_factor_built_in_energy = i32(31661, gain=1000)
    apparent_power_built_in_energy = i32(31663, unit="VA")
    phase_a_active_power_built_in_energy = i32(31665, unit="W")
    phase_b_active_power_built_in_energy = i32(31667, unit="W")
    phase_c_active_power_built_in_energy = i32(31669, unit="W")
    total_active_energy_built_in_energy = i64(31671, unit="kWh", gain=100)
    total_negative_active_energy_built_in_energy = i64(31679, unit="kWh", gain=100)
    total_positive_active_energy_built_in_energy = i64(31687, unit="kWh", gain=100)


class EmmaSettings(HuaweiComponent):
    """EMMA configuration: control mode, schedules and clock."""

    emma_ess_control_mode = i16(40000, convert=rv.EmmaEssControlMode, writable=True)
    emma_tou_preferred_use_of_surplus_pv_power = u16(40001, convert=rv.StorageExcessPvEnergyUseInTOU, writable=True)
    emma_tou_maximum_power_for_charging_batteries_from_grid = u32(40002, unit="W", writable=True)
    emma_tou_periods = HuaweiLuna2000TimeOfUseField(40004, count=43, writable=True)
    emma_power_control_mode_at_grid_connection_point = u16(40100, convert=rv.ActivePowerControlMode, writable=True)
    emma_limitation_mode = u16(40101, convert=rv.EmmaLimitationMode, writable=True)
    emma_maximum_feed_grid_power_watt = i32(40107, unit="W", writable=True)
    emma_maximum_feed_grid_power_percent = u16(40109, unit="%", gain=10, writable=True)
    emma_3phase_imbalance_control = u16(40110, convert=bool, writable=True)
    emma_system_time = u32(40470, unit="seconds", writable=True)
    local_time_year = u16(40490, writable=True)
    emma_power_supply_configuration = u16(41214, convert=rv.EmmaPowerSupplyConfiguration, writable=True)
    emma_consider_mains_faulty_if = u16(41215, convert=rv.EmmaConsiderMainsFaultyIf, writable=True)
    emma = u16(48020, convert=bool, writable=True)
