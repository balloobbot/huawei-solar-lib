"""Where each published Huawei register name lives in the component model.

Home Assistant addresses registers by the name Huawei publishes — an entity
is configured with one, and services take one from a service call — while a
component addresses them as attributes. This table is the bridge, and is
generated from the register map so the two cannot drift apart.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, NamedTuple

from huawei_solar.components import emma, scharger, sdongle, shared, smartlogger, sun2000

if TYPE_CHECKING:
    from modbus_connection.model import RegisterField

    from huawei_solar.components.base import HuaweiComponent


class RegisterLocation(NamedTuple):
    """The component field a published register name resolves to."""

    component: type[HuaweiComponent]
    """The component class declaring the field."""

    field: str
    """The attribute name on that component."""

    instance: int | None
    """Which instance, for a component that exists once per string, unit or pack."""

    def definition(self) -> RegisterField[Any]:
        """Return the field object itself.

        A method rather than a property on purpose: ``RegisterField`` is a
        descriptor, and a type checker applies its ``__get__`` to anything typed
        as one that is reached by attribute access — re-typing the field object
        itself as the value it decodes to. Calling for it sidesteps that.
        """
        return self.component.declared_fields[self.field]  # type: ignore[return-value]


REGISTER_LOCATIONS: dict[str, RegisterLocation] = {
    "P_max": RegisterLocation(sun2000.ProductInfo, "P_max", None),
    "P_max_real": RegisterLocation(sun2000.ProductInfo, "P_max_real", None),
    "Q_max_in": RegisterLocation(sun2000.ProductInfo, "Q_max_in", None),
    "Q_max_out": RegisterLocation(sun2000.ProductInfo, "Q_max_out", None),
    "S_max": RegisterLocation(sun2000.ProductInfo, "S_max", None),
    "S_max_real": RegisterLocation(sun2000.ProductInfo, "S_max_real", None),
    "ac_terminal_1_2_3_max_temp": RegisterLocation(sun2000.Diagnostics, "ac_terminal_1_2_3_max_temp", None),
    "accumulated_yield_energy": RegisterLocation(sun2000.Inverter, "accumulated_yield_energy", None),
    "active_grid_A_B_voltage": RegisterLocation(sun2000.PowerMeter, "active_grid_A_B_voltage", None),
    "active_grid_A_current": RegisterLocation(sun2000.PowerMeter, "active_grid_A_current", None),
    "active_grid_A_power": RegisterLocation(sun2000.PowerMeter, "active_grid_A_power", None),
    "active_grid_B_C_voltage": RegisterLocation(sun2000.PowerMeter, "active_grid_B_C_voltage", None),
    "active_grid_B_current": RegisterLocation(sun2000.PowerMeter, "active_grid_B_current", None),
    "active_grid_B_power": RegisterLocation(sun2000.PowerMeter, "active_grid_B_power", None),
    "active_grid_C_A_voltage": RegisterLocation(sun2000.PowerMeter, "active_grid_C_A_voltage", None),
    "active_grid_C_current": RegisterLocation(sun2000.PowerMeter, "active_grid_C_current", None),
    "active_grid_C_power": RegisterLocation(sun2000.PowerMeter, "active_grid_C_power", None),
    "active_grid_frequency": RegisterLocation(sun2000.PowerMeter, "active_grid_frequency", None),
    "active_grid_power_factor": RegisterLocation(sun2000.PowerMeter, "active_grid_power_factor", None),
    "active_power": RegisterLocation(sun2000.Inverter, "active_power", None),
    "active_power_adjustment_command": RegisterLocation(sun2000.Diagnostics, "active_power_adjustment_command", None),
    "active_power_adjustment_mode": RegisterLocation(sun2000.Diagnostics, "active_power_adjustment_mode", None),
    "active_power_adjustment_value": RegisterLocation(sun2000.Diagnostics, "active_power_adjustment_value", None),
    "active_power_built_in_energy": RegisterLocation(emma.EmmaBuiltInMeter, "active_power_built_in_energy", None),
    "active_power_control_mode": RegisterLocation(sun2000.Configuration, "active_power_control_mode", None),
    "active_power_external_energy": RegisterLocation(emma.EmmaExternalMeter, "active_power_external_energy", None),
    "active_power_fast": RegisterLocation(sun2000.Inverter, "active_power_fast", None),
    "active_power_fixed_value_derating": RegisterLocation(
        sun2000.Configuration, "active_power_fixed_value_derating", None
    ),
    "active_power_percentage_derating": RegisterLocation(
        sun2000.Configuration, "active_power_percentage_derating", None
    ),
    "afci_2_version": RegisterLocation(sun2000.ProductInfo, "afci_2_version", None),
    "afci_version": RegisterLocation(sun2000.ProductInfo, "afci_version", None),
    "alarm_1": RegisterLocation(sun2000.Inverter, "alarm_1", None),
    "alarm_2": RegisterLocation(sun2000.Inverter, "alarm_2", None),
    "alarm_3": RegisterLocation(sun2000.Inverter, "alarm_3", None),
    "annual_energy_consumption": RegisterLocation(emma.Emma, "annual_energy_consumption", None),
    "anti_reverse_module_1_temp": RegisterLocation(sun2000.Diagnostics, "anti_reverse_module_1_temp", None),
    "anti_reverse_module_2_temp": RegisterLocation(sun2000.Diagnostics, "anti_reverse_module_2_temp", None),
    "apparent_power_built_in_energy": RegisterLocation(emma.EmmaBuiltInMeter, "apparent_power_built_in_energy", None),
    "apparent_power_external_energy": RegisterLocation(emma.EmmaExternalMeter, "apparent_power_external_energy", None),
    "average_pv_negative_voltage_to_ground": RegisterLocation(
        sun2000.Inverter, "average_pv_negative_voltage_to_ground", None
    ),
    "backup_power_state_of_charge": RegisterLocation(emma.Emma, "backup_power_state_of_charge", None),
    "backup_switch_to_off_grid": RegisterLocation(sun2000.Configuration, "backup_switch_to_off_grid", None),
    "backup_time_notification_threshold": RegisterLocation(emma.Emma, "backup_time_notification_threshold", None),
    "backup_voltage_independent_operation": RegisterLocation(
        sun2000.Configuration, "backup_voltage_independent_operation", None
    ),
    "battery_charge_discharge_power": RegisterLocation(emma.Emma, "battery_charge_discharge_power", None),
    "builtin_pid_running_status": RegisterLocation(sun2000.Inverter, "builtin_pid_running_status", None),
    "builtin_pid_version": RegisterLocation(sun2000.ProductInfo, "builtin_pid_version", None),
    "bus_negative_voltage_to_ground": RegisterLocation(sun2000.Diagnostics, "bus_negative_voltage_to_ground", None),
    "capbank_running_time": RegisterLocation(sun2000.Diagnostics, "capbank_running_time", None),
    "characteristic_curve_reactive_power_adjustment_time": RegisterLocation(
        sun2000.Configuration, "characteristic_curve_reactive_power_adjustment_time", None
    ),
    "charger_model": RegisterLocation(scharger.SCharger, "model", None),
    "charger_phase_a_voltage": RegisterLocation(scharger.SCharger, "phase_a_voltage", None),
    "charger_phase_b_voltage": RegisterLocation(scharger.SCharger, "phase_b_voltage", None),
    "charger_phase_c_voltage": RegisterLocation(scharger.SCharger, "phase_c_voltage", None),
    "charger_rated_power": RegisterLocation(scharger.SCharger, "rated_power", None),
    "charger_serial_number": RegisterLocation(scharger.SCharger, "serial_number", None),
    "charger_software_version": RegisterLocation(scharger.SCharger, "software_version", None),
    "charger_temperature": RegisterLocation(scharger.SCharger, "temperature", None),
    "charger_total_energy_charged": RegisterLocation(scharger.SCharger, "total_energy_charged", None),
    "consumption_today": RegisterLocation(emma.Emma, "consumption_today", None),
    "cpld_version": RegisterLocation(sun2000.ProductInfo, "cpld_version", None),
    "cumulative_dc_energy_yield_mppt1": RegisterLocation(sun2000.Inverter, "cumulative_dc_energy_yield_mppt1", None),
    "cumulative_dc_energy_yield_mppt10": RegisterLocation(sun2000.Inverter, "cumulative_dc_energy_yield_mppt10", None),
    "cumulative_dc_energy_yield_mppt2": RegisterLocation(sun2000.Inverter, "cumulative_dc_energy_yield_mppt2", None),
    "cumulative_dc_energy_yield_mppt3": RegisterLocation(sun2000.Inverter, "cumulative_dc_energy_yield_mppt3", None),
    "cumulative_dc_energy_yield_mppt4": RegisterLocation(sun2000.Inverter, "cumulative_dc_energy_yield_mppt4", None),
    "cumulative_dc_energy_yield_mppt5": RegisterLocation(sun2000.Inverter, "cumulative_dc_energy_yield_mppt5", None),
    "cumulative_dc_energy_yield_mppt6": RegisterLocation(sun2000.Inverter, "cumulative_dc_energy_yield_mppt6", None),
    "cumulative_dc_energy_yield_mppt7": RegisterLocation(sun2000.Inverter, "cumulative_dc_energy_yield_mppt7", None),
    "cumulative_dc_energy_yield_mppt8": RegisterLocation(sun2000.Inverter, "cumulative_dc_energy_yield_mppt8", None),
    "cumulative_dc_energy_yield_mppt9": RegisterLocation(sun2000.Inverter, "cumulative_dc_energy_yield_mppt9", None),
    "current_electricity_generation_statistics_time": RegisterLocation(
        sun2000.Inverter, "current_electricity_generation_statistics_time", None
    ),
    "daily_yield_energy": RegisterLocation(sun2000.Inverter, "daily_yield_energy", None),
    "day_active_power_peak": RegisterLocation(sun2000.Inverter, "day_active_power_peak", None),
    "daylight_saving_time": RegisterLocation(shared.DeviceIdentity, "daylight_saving_time", None),
    "dc_mbus_version": RegisterLocation(sun2000.ProductInfo, "dc_mbus_version", None),
    "dc_terminal_1_2_max_temp": RegisterLocation(sun2000.Diagnostics, "dc_terminal_1_2_max_temp", None),
    "default_active_power_change_gradient": RegisterLocation(
        sun2000.Configuration, "default_active_power_change_gradient", None
    ),
    "default_maximum_feed_in_power": RegisterLocation(sun2000.Configuration, "default_maximum_feed_in_power", None),
    "device_status": RegisterLocation(sun2000.Inverter, "device_status", None),
    "dongle_plant_maximum_charge_from_grid_power": RegisterLocation(
        sun2000.Configuration, "dongle_plant_maximum_charge_from_grid_power", None
    ),
    "efficiency": RegisterLocation(sun2000.Inverter, "efficiency", None),
    "el_module_version": RegisterLocation(sun2000.ProductInfo, "el_module_version", None),
    "emma": RegisterLocation(emma.EmmaSettings, "emma", None),
    "emma_3phase_imbalance_control": RegisterLocation(emma.EmmaSettings, "emma_3phase_imbalance_control", None),
    "emma_consider_mains_faulty_if": RegisterLocation(emma.EmmaSettings, "emma_consider_mains_faulty_if", None),
    "emma_dst_state": RegisterLocation(emma.Emma, "emma_dst_state", None),
    "emma_ess_control_mode": RegisterLocation(emma.EmmaSettings, "emma_ess_control_mode", None),
    "emma_external_meter_active_power": RegisterLocation(
        emma.EmmaExternalMeter, "emma_external_meter_active_power", None
    ),
    "emma_external_meter_apparent_power": RegisterLocation(
        emma.EmmaExternalMeter, "emma_external_meter_apparent_power", None
    ),
    "emma_external_meter_line_voltage_a_b": RegisterLocation(
        emma.EmmaExternalMeter, "emma_external_meter_line_voltage_a_b", None
    ),
    "emma_external_meter_line_voltage_b_c": RegisterLocation(
        emma.EmmaExternalMeter, "emma_external_meter_line_voltage_b_c", None
    ),
    "emma_external_meter_line_voltage_c_a": RegisterLocation(
        emma.EmmaExternalMeter, "emma_external_meter_line_voltage_c_a", None
    ),
    "emma_external_meter_phase_a_active_power": RegisterLocation(
        emma.EmmaExternalMeter, "emma_external_meter_phase_a_active_power", None
    ),
    "emma_external_meter_phase_a_current": RegisterLocation(
        emma.EmmaExternalMeter, "emma_external_meter_phase_a_current", None
    ),
    "emma_external_meter_phase_a_voltage": RegisterLocation(
        emma.EmmaExternalMeter, "emma_external_meter_phase_a_voltage", None
    ),
    "emma_external_meter_phase_b_active_power": RegisterLocation(
        emma.EmmaExternalMeter, "emma_external_meter_phase_b_active_power", None
    ),
    "emma_external_meter_phase_b_current": RegisterLocation(
        emma.EmmaExternalMeter, "emma_external_meter_phase_b_current", None
    ),
    "emma_external_meter_phase_b_voltage": RegisterLocation(
        emma.EmmaExternalMeter, "emma_external_meter_phase_b_voltage", None
    ),
    "emma_external_meter_phase_c_active_power": RegisterLocation(
        emma.EmmaExternalMeter, "emma_external_meter_phase_c_active_power", None
    ),
    "emma_external_meter_phase_c_current": RegisterLocation(
        emma.EmmaExternalMeter, "emma_external_meter_phase_c_current", None
    ),
    "emma_external_meter_phase_c_voltage": RegisterLocation(
        emma.EmmaExternalMeter, "emma_external_meter_phase_c_voltage", None
    ),
    "emma_external_meter_power_factor": RegisterLocation(
        emma.EmmaExternalMeter, "emma_external_meter_power_factor", None
    ),
    "emma_external_meter_running_status": RegisterLocation(
        emma.EmmaExternalMeter, "emma_external_meter_running_status", None
    ),
    "emma_external_meter_total_active_energy": RegisterLocation(
        emma.EmmaExternalMeter, "emma_external_meter_total_active_energy", None
    ),
    "emma_external_meter_total_negative_active_energy": RegisterLocation(
        emma.EmmaExternalMeter, "emma_external_meter_total_negative_active_energy", None
    ),
    "emma_external_meter_total_positive_active_energy": RegisterLocation(
        emma.EmmaExternalMeter, "emma_external_meter_total_positive_active_energy", None
    ),
    "emma_limitation_mode": RegisterLocation(emma.EmmaSettings, "emma_limitation_mode", None),
    "emma_local_time": RegisterLocation(emma.Emma, "emma_local_time", None),
    "emma_maximum_feed_grid_power_percent": RegisterLocation(
        emma.EmmaSettings, "emma_maximum_feed_grid_power_percent", None
    ),
    "emma_maximum_feed_grid_power_watt": RegisterLocation(emma.EmmaSettings, "emma_maximum_feed_grid_power_watt", None),
    "emma_model": RegisterLocation(emma.Emma, "emma_model", None),
    "emma_power_control_mode_at_grid_connection_point": RegisterLocation(
        emma.EmmaSettings, "emma_power_control_mode_at_grid_connection_point", None
    ),
    "emma_power_supply_configuration": RegisterLocation(emma.EmmaSettings, "emma_power_supply_configuration", None),
    "emma_software_version": RegisterLocation(emma.Emma, "emma_software_version", None),
    "emma_system_time": RegisterLocation(emma.EmmaSettings, "emma_system_time", None),
    "emma_tou_maximum_power_for_charging_batteries_from_grid": RegisterLocation(
        emma.EmmaSettings, "emma_tou_maximum_power_for_charging_batteries_from_grid", None
    ),
    "emma_tou_periods": RegisterLocation(emma.EmmaSettings, "emma_tou_periods", None),
    "emma_tou_preferred_use_of_surplus_pv_power": RegisterLocation(
        emma.EmmaSettings, "emma_tou_preferred_use_of_surplus_pv_power", None
    ),
    "energy_charged_this_month": RegisterLocation(emma.Emma, "energy_charged_this_month", None),
    "energy_charged_today": RegisterLocation(emma.Emma, "energy_charged_today", None),
    "energy_discharged_this_month": RegisterLocation(emma.Emma, "energy_discharged_this_month", None),
    "energy_discharged_today": RegisterLocation(emma.Emma, "energy_discharged_today", None),
    "ess_chargeable_capacity": RegisterLocation(emma.Emma, "ess_chargeable_capacity", None),
    "ess_chargeable_energy": RegisterLocation(emma.Emma, "ess_chargeable_energy", None),
    "ess_dischargeable_capacity": RegisterLocation(emma.Emma, "ess_dischargeable_capacity", None),
    "ess_dischargeable_energy": RegisterLocation(emma.Emma, "ess_dischargeable_energy", None),
    "fault_code": RegisterLocation(sun2000.Inverter, "fault_code", None),
    "feature_mask_1": RegisterLocation(sun2000.ProductInfo, "feature_mask_1", None),
    "feature_mask_2": RegisterLocation(sun2000.ProductInfo, "feature_mask_2", None),
    "feature_mask_3": RegisterLocation(sun2000.ProductInfo, "feature_mask_3", None),
    "feature_mask_4": RegisterLocation(sun2000.ProductInfo, "feature_mask_4", None),
    "feed_in_power": RegisterLocation(emma.Emma, "feed_in_power", None),
    "feed_in_to_grid_today": RegisterLocation(emma.Emma, "feed_in_to_grid_today", None),
    "firmware_version": RegisterLocation(sun2000.ProductInfo, "firmware_version", None),
    "fixed_reactive_power_at_night": RegisterLocation(sun2000.Configuration, "fixed_reactive_power_at_night", None),
    "forcible_charge_discharge_write": RegisterLocation(sun2000.Configuration, "forcible_charge_discharge_write", None),
    "grid_A_voltage": RegisterLocation(sun2000.PowerMeter, "grid_A_voltage", None),
    "grid_B_voltage": RegisterLocation(sun2000.PowerMeter, "grid_B_voltage", None),
    "grid_C_voltage": RegisterLocation(sun2000.PowerMeter, "grid_C_voltage", None),
    "grid_accumulated_energy": RegisterLocation(sun2000.PowerMeter, "grid_accumulated_energy", None),
    "grid_accumulated_reactive_power": RegisterLocation(sun2000.PowerMeter, "grid_accumulated_reactive_power", None),
    "grid_code": RegisterLocation(sun2000.Configuration, "grid_code", None),
    "grid_current": RegisterLocation(sun2000.Inverter, "grid_current", None),
    "grid_exported_energy": RegisterLocation(sun2000.PowerMeter, "grid_exported_energy", None),
    "grid_frequency": RegisterLocation(sun2000.Inverter, "grid_frequency", None),
    "grid_standard_code_protocol_version": RegisterLocation(
        sun2000.ProductInfo, "grid_standard_code_protocol_version", None
    ),
    "grid_voltage": RegisterLocation(sun2000.Inverter, "grid_voltage", None),
    "hardware_functional_unit_conf_id": RegisterLocation(sun2000.ProductInfo, "hardware_functional_unit_conf_id", None),
    "hardware_version": RegisterLocation(sun2000.ProductInfo, "hardware_version", None),
    "hourly_yield_energy": RegisterLocation(sun2000.Inverter, "hourly_yield_energy", None),
    "input_power": RegisterLocation(sun2000.Inverter, "input_power", None),
    "insulation_resistance": RegisterLocation(sun2000.Inverter, "insulation_resistance", None),
    "internal_fan_1_running_time": RegisterLocation(sun2000.Diagnostics, "internal_fan_1_running_time", None),
    "internal_temperature": RegisterLocation(sun2000.Inverter, "internal_temperature", None),
    "inv_module_a_temp": RegisterLocation(sun2000.Diagnostics, "inv_module_a_temp", None),
    "inv_module_b_temp": RegisterLocation(sun2000.Diagnostics, "inv_module_b_temp", None),
    "inv_module_c_temp": RegisterLocation(sun2000.Diagnostics, "inv_module_c_temp", None),
    "inverter_active_power": RegisterLocation(emma.Emma, "inverter_active_power", None),
    "inverter_energy_yield_today": RegisterLocation(emma.Emma, "inverter_energy_yield_today", None),
    "inverter_rated_power": RegisterLocation(emma.Emma, "inverter_rated_power", None),
    "inverter_to_pe_voltage_tolerance": RegisterLocation(sun2000.Inverter, "inverter_to_pe_voltage_tolerance", None),
    "inverter_total_absorbed_energy": RegisterLocation(emma.Emma, "inverter_total_absorbed_energy", None),
    "inverter_total_energy_yield": RegisterLocation(emma.Emma, "inverter_total_energy_yield", None),
    "iso_feature_information": RegisterLocation(sun2000.Inverter, "iso_feature_information", None),
    "latest_active_alarm_sn": RegisterLocation(sun2000.Inverter, "latest_active_alarm_sn", None),
    "latest_historical_alarm_sn": RegisterLocation(sun2000.Inverter, "latest_historical_alarm_sn", None),
    "leakage_current_rcd": RegisterLocation(sun2000.Diagnostics, "leakage_current_rcd", None),
    "line_voltage_A_B": RegisterLocation(sun2000.Inverter, "line_voltage_A_B", None),
    "line_voltage_B_C": RegisterLocation(sun2000.Inverter, "line_voltage_B_C", None),
    "line_voltage_C_A": RegisterLocation(sun2000.Inverter, "line_voltage_C_A", None),
    "line_voltage_a_b_built_in_energy": RegisterLocation(
        emma.EmmaBuiltInMeter, "line_voltage_a_b_built_in_energy", None
    ),
    "line_voltage_a_b_external_energy": RegisterLocation(
        emma.EmmaExternalMeter, "line_voltage_a_b_external_energy", None
    ),
    "line_voltage_b_c_built_in_energy": RegisterLocation(
        emma.EmmaBuiltInMeter, "line_voltage_b_c_built_in_energy", None
    ),
    "line_voltage_b_c_external_energy": RegisterLocation(
        emma.EmmaExternalMeter, "line_voltage_b_c_external_energy", None
    ),
    "line_voltage_c_a_built_in_energy": RegisterLocation(
        emma.EmmaBuiltInMeter, "line_voltage_c_a_built_in_energy", None
    ),
    "line_voltage_c_a_external_energy": RegisterLocation(
        emma.EmmaExternalMeter, "line_voltage_c_a_external_energy", None
    ),
    "load_power": RegisterLocation(emma.Emma, "load_power", None),
    "local_time_year": RegisterLocation(emma.EmmaSettings, "local_time_year", None),
    "master_dsp_version": RegisterLocation(sun2000.ProductInfo, "master_dsp_version", None),
    "max_pv_negative_voltage_to_ground": RegisterLocation(sun2000.Inverter, "max_pv_negative_voltage_to_ground", None),
    "max_pv_voltage": RegisterLocation(sun2000.Inverter, "max_pv_voltage", None),
    "maximum_active_power": RegisterLocation(sun2000.Configuration, "maximum_active_power", None),
    "maximum_feed_grid_power_percent": RegisterLocation(sun2000.Configuration, "maximum_feed_grid_power_percent", None),
    "maximum_feed_grid_power_watt": RegisterLocation(sun2000.Configuration, "maximum_feed_grid_power_watt", None),
    "meter_status": RegisterLocation(sun2000.PowerMeter, "meter_status", None),
    "meter_type": RegisterLocation(sun2000.PowerMeter, "meter_type", None),
    "meter_type_check": RegisterLocation(sun2000.PowerMeter, "meter_type_check", None),
    "min_pv_negative_voltage_to_ground": RegisterLocation(sun2000.Inverter, "min_pv_negative_voltage_to_ground", None),
    "min_pv_voltage": RegisterLocation(sun2000.Inverter, "min_pv_voltage", None),
    "model_id": RegisterLocation(sun2000.ProductInfo, "model_id", None),
    "model_name": RegisterLocation(shared.DeviceIdentity, "model_name", None),
    "monitoring_board_sn": RegisterLocation(sun2000.ProductInfo, "monitoring_board_sn", None),
    "monitoring_software_version": RegisterLocation(sun2000.ProductInfo, "monitoring_software_version", None),
    "monthly_energy_consumption": RegisterLocation(emma.Emma, "monthly_energy_consumption", None),
    "monthly_feed_in_to_grid": RegisterLocation(emma.Emma, "monthly_feed_in_to_grid", None),
    "monthly_supply_from_grid": RegisterLocation(emma.Emma, "monthly_supply_from_grid", None),
    "monthly_yield_energy": RegisterLocation(sun2000.Inverter, "monthly_yield_energy", None),
    "mppt_multimodal_scanning": RegisterLocation(sun2000.Configuration, "mppt_multimodal_scanning", None),
    "mppt_predicted_power": RegisterLocation(sun2000.Configuration, "mppt_predicted_power", None),
    "mppt_scanning_interval": RegisterLocation(sun2000.Configuration, "mppt_scanning_interval", None),
    "nb_mpp_tracks": RegisterLocation(sun2000.ProductInfo, "nb_mpp_tracks", None),
    "nb_online_optimizers": RegisterLocation(sun2000.Optimizers, "nb_online_optimizers", None),
    "nb_optimizers": RegisterLocation(sun2000.Optimizers, "nb_optimizers", None),
    "nb_pv_strings": RegisterLocation(sun2000.ProductInfo, "nb_pv_strings", None),
    "negative_bus_voltage": RegisterLocation(sun2000.Diagnostics, "negative_bus_voltage", None),
    "number_of_chargers_found": RegisterLocation(emma.Emma, "number_of_chargers_found", None),
    "number_of_inverters_found": RegisterLocation(emma.Emma, "number_of_inverters_found", None),
    "number_of_packages_to_be_upgraded": RegisterLocation(
        sun2000.ProductInfo, "number_of_packages_to_be_upgraded", None
    ),
    "offering_name_of_southbound_device_1": RegisterLocation(
        sun2000.ProductInfo, "offering_name_of_southbound_device_1", None
    ),
    "offering_name_of_southbound_device_2": RegisterLocation(
        sun2000.ProductInfo, "offering_name_of_southbound_device_2", None
    ),
    "offering_name_of_southbound_device_3": RegisterLocation(
        sun2000.ProductInfo, "offering_name_of_southbound_device_3", None
    ),
    "output_board_relay_ambient_temp_max": RegisterLocation(
        sun2000.Diagnostics, "output_board_relay_ambient_temp_max", None
    ),
    "percent_apparent_power": RegisterLocation(sun2000.Configuration, "percent_apparent_power", None),
    "phase_A_current": RegisterLocation(sun2000.Inverter, "phase_A_current", None),
    "phase_A_voltage": RegisterLocation(sun2000.Inverter, "phase_A_voltage", None),
    "phase_B_current": RegisterLocation(sun2000.Inverter, "phase_B_current", None),
    "phase_B_voltage": RegisterLocation(sun2000.Inverter, "phase_B_voltage", None),
    "phase_C_current": RegisterLocation(sun2000.Inverter, "phase_C_current", None),
    "phase_C_voltage": RegisterLocation(sun2000.Inverter, "phase_C_voltage", None),
    "phase_a_active_power_built_in_energy": RegisterLocation(
        emma.EmmaBuiltInMeter, "phase_a_active_power_built_in_energy", None
    ),
    "phase_a_active_power_external_energy": RegisterLocation(
        emma.EmmaExternalMeter, "phase_a_active_power_external_energy", None
    ),
    "phase_a_current_built_in_energy": RegisterLocation(emma.EmmaBuiltInMeter, "phase_a_current_built_in_energy", None),
    "phase_a_current_external_energy": RegisterLocation(
        emma.EmmaExternalMeter, "phase_a_current_external_energy", None
    ),
    "phase_a_dc_component_dci": RegisterLocation(sun2000.Diagnostics, "phase_a_dc_component_dci", None),
    "phase_a_voltage_built_in_energy": RegisterLocation(emma.EmmaBuiltInMeter, "phase_a_voltage_built_in_energy", None),
    "phase_a_voltage_external_energy": RegisterLocation(
        emma.EmmaExternalMeter, "phase_a_voltage_external_energy", None
    ),
    "phase_b_active_power_built_in_energy": RegisterLocation(
        emma.EmmaBuiltInMeter, "phase_b_active_power_built_in_energy", None
    ),
    "phase_b_active_power_external_energy": RegisterLocation(
        emma.EmmaExternalMeter, "phase_b_active_power_external_energy", None
    ),
    "phase_b_current_built_in_energy": RegisterLocation(emma.EmmaBuiltInMeter, "phase_b_current_built_in_energy", None),
    "phase_b_current_external_energy": RegisterLocation(
        emma.EmmaExternalMeter, "phase_b_current_external_energy", None
    ),
    "phase_b_dc_component_dci": RegisterLocation(sun2000.Diagnostics, "phase_b_dc_component_dci", None),
    "phase_b_voltage_built_in_energy": RegisterLocation(emma.EmmaBuiltInMeter, "phase_b_voltage_built_in_energy", None),
    "phase_b_voltage_external_energy": RegisterLocation(
        emma.EmmaExternalMeter, "phase_b_voltage_external_energy", None
    ),
    "phase_c_active_power_built_in_energy": RegisterLocation(
        emma.EmmaBuiltInMeter, "phase_c_active_power_built_in_energy", None
    ),
    "phase_c_active_power_external_energy": RegisterLocation(
        emma.EmmaExternalMeter, "phase_c_active_power_external_energy", None
    ),
    "phase_c_current_built_in_energy": RegisterLocation(emma.EmmaBuiltInMeter, "phase_c_current_built_in_energy", None),
    "phase_c_current_external_energy": RegisterLocation(
        emma.EmmaExternalMeter, "phase_c_current_external_energy", None
    ),
    "phase_c_dc_component_dci": RegisterLocation(sun2000.Diagnostics, "phase_c_dc_component_dci", None),
    "phase_c_voltage_built_in_energy": RegisterLocation(emma.EmmaBuiltInMeter, "phase_c_voltage_built_in_energy", None),
    "phase_c_voltage_external_energy": RegisterLocation(
        emma.EmmaExternalMeter, "phase_c_voltage_external_energy", None
    ),
    "pn": RegisterLocation(sun2000.ProductInfo, "pn", None),
    "positive_bus_voltage": RegisterLocation(sun2000.Diagnostics, "positive_bus_voltage", None),
    "power_factor": RegisterLocation(sun2000.Inverter, "power_factor", None),
    "power_factor_2": RegisterLocation(sun2000.Configuration, "power_factor_2", None),
    "power_factor_built_in_energy": RegisterLocation(emma.EmmaBuiltInMeter, "power_factor_built_in_energy", None),
    "power_factor_external_energy": RegisterLocation(emma.EmmaExternalMeter, "power_factor_external_energy", None),
    "power_meter_active_power": RegisterLocation(sun2000.PowerMeter, "power_meter_active_power", None),
    "power_meter_reactive_power": RegisterLocation(sun2000.PowerMeter, "power_meter_reactive_power", None),
    "product_sales_area": RegisterLocation(sun2000.ProductInfo, "product_sales_area", None),
    "product_software_number": RegisterLocation(sun2000.ProductInfo, "product_software_number", None),
    "product_software_version_number": RegisterLocation(sun2000.ProductInfo, "product_software_version_number", None),
    "protocol_version_modbus": RegisterLocation(sun2000.ProductInfo, "protocol_version_modbus", None),
    "pv_01_current": RegisterLocation(sun2000.PVString, "current", 1),
    "pv_01_voltage": RegisterLocation(sun2000.PVString, "voltage", 1),
    "pv_02_current": RegisterLocation(sun2000.PVString, "current", 2),
    "pv_02_voltage": RegisterLocation(sun2000.PVString, "voltage", 2),
    "pv_03_current": RegisterLocation(sun2000.PVString, "current", 3),
    "pv_03_voltage": RegisterLocation(sun2000.PVString, "voltage", 3),
    "pv_04_current": RegisterLocation(sun2000.PVString, "current", 4),
    "pv_04_voltage": RegisterLocation(sun2000.PVString, "voltage", 4),
    "pv_05_current": RegisterLocation(sun2000.PVString, "current", 5),
    "pv_05_voltage": RegisterLocation(sun2000.PVString, "voltage", 5),
    "pv_06_current": RegisterLocation(sun2000.PVString, "current", 6),
    "pv_06_voltage": RegisterLocation(sun2000.PVString, "voltage", 6),
    "pv_07_current": RegisterLocation(sun2000.PVString, "current", 7),
    "pv_07_voltage": RegisterLocation(sun2000.PVString, "voltage", 7),
    "pv_08_current": RegisterLocation(sun2000.PVString, "current", 8),
    "pv_08_voltage": RegisterLocation(sun2000.PVString, "voltage", 8),
    "pv_09_current": RegisterLocation(sun2000.PVString, "current", 9),
    "pv_09_voltage": RegisterLocation(sun2000.PVString, "voltage", 9),
    "pv_10_current": RegisterLocation(sun2000.PVString, "current", 10),
    "pv_10_voltage": RegisterLocation(sun2000.PVString, "voltage", 10),
    "pv_11_current": RegisterLocation(sun2000.PVString, "current", 11),
    "pv_11_voltage": RegisterLocation(sun2000.PVString, "voltage", 11),
    "pv_12_current": RegisterLocation(sun2000.PVString, "current", 12),
    "pv_12_voltage": RegisterLocation(sun2000.PVString, "voltage", 12),
    "pv_13_current": RegisterLocation(sun2000.PVString, "current", 13),
    "pv_13_voltage": RegisterLocation(sun2000.PVString, "voltage", 13),
    "pv_14_current": RegisterLocation(sun2000.PVString, "current", 14),
    "pv_14_voltage": RegisterLocation(sun2000.PVString, "voltage", 14),
    "pv_15_current": RegisterLocation(sun2000.PVString, "current", 15),
    "pv_15_voltage": RegisterLocation(sun2000.PVString, "voltage", 15),
    "pv_16_current": RegisterLocation(sun2000.PVString, "current", 16),
    "pv_16_voltage": RegisterLocation(sun2000.PVString, "voltage", 16),
    "pv_17_current": RegisterLocation(sun2000.PVString, "current", 17),
    "pv_17_voltage": RegisterLocation(sun2000.PVString, "voltage", 17),
    "pv_18_current": RegisterLocation(sun2000.PVString, "current", 18),
    "pv_18_voltage": RegisterLocation(sun2000.PVString, "voltage", 18),
    "pv_19_current": RegisterLocation(sun2000.PVString, "current", 19),
    "pv_19_voltage": RegisterLocation(sun2000.PVString, "voltage", 19),
    "pv_20_current": RegisterLocation(sun2000.PVString, "current", 20),
    "pv_20_voltage": RegisterLocation(sun2000.PVString, "voltage", 20),
    "pv_21_current": RegisterLocation(sun2000.PVString, "current", 21),
    "pv_21_voltage": RegisterLocation(sun2000.PVString, "voltage", 21),
    "pv_22_current": RegisterLocation(sun2000.PVString, "current", 22),
    "pv_22_voltage": RegisterLocation(sun2000.PVString, "voltage", 22),
    "pv_23_current": RegisterLocation(sun2000.PVString, "current", 23),
    "pv_23_voltage": RegisterLocation(sun2000.PVString, "voltage", 23),
    "pv_24_current": RegisterLocation(sun2000.PVString, "current", 24),
    "pv_24_voltage": RegisterLocation(sun2000.PVString, "voltage", 24),
    "pv_negative_voltage_to_ground": RegisterLocation(sun2000.Inverter, "pv_negative_voltage_to_ground", None),
    "pv_output_power": RegisterLocation(emma.Emma, "pv_output_power", None),
    "pv_yield_today": RegisterLocation(emma.Emma, "pv_yield_today", None),
    "q_u_characteristic_curve_model": RegisterLocation(sun2000.Configuration, "q_u_characteristic_curve_model", None),
    "q_u_scheduling_exit_power_percentage": RegisterLocation(
        sun2000.Configuration, "q_u_scheduling_exit_power_percentage", None
    ),
    "q_u_scheduling_trigger_power_percentage": RegisterLocation(
        sun2000.Configuration, "q_u_scheduling_trigger_power_percentage", None
    ),
    "rated_ess_capacity": RegisterLocation(emma.Emma, "rated_ess_capacity", None),
    "rated_power": RegisterLocation(sun2000.ProductInfo, "rated_power", None),
    "reactive_power": RegisterLocation(sun2000.Inverter, "reactive_power", None),
    "reactive_power_adjustment_time": RegisterLocation(sun2000.Configuration, "reactive_power_adjustment_time", None),
    "reactive_power_compensation": RegisterLocation(sun2000.Configuration, "reactive_power_compensation", None),
    "reactive_power_compensation_at_night": RegisterLocation(
        sun2000.Configuration, "reactive_power_compensation_at_night", None
    ),
    "realtime_max_active_capability": RegisterLocation(sun2000.ProductInfo, "realtime_max_active_capability", None),
    "realtime_max_inductive_reactive_capacity": RegisterLocation(
        sun2000.ProductInfo, "realtime_max_inductive_reactive_capacity", None
    ),
    "regkey": RegisterLocation(sun2000.ProductInfo, "regkey", None),
    "remote_charge_discharge_control_mode": RegisterLocation(
        sun2000.Configuration, "remote_charge_discharge_control_mode", None
    ),
    "sdongle_application_layer_heartbeat_period": RegisterLocation(
        sdongle.SDongle, "application_layer_heartbeat_period", None
    ),
    "sdongle_average_daily_used_traffic_4g": RegisterLocation(sdongle.SDongle, "average_daily_used_traffic_4g", None),
    "sdongle_card_number_4g": RegisterLocation(sdongle.SDongle, "card_number_4g", None),
    "sdongle_carrier_4g": RegisterLocation(sdongle.SDongle, "carrier_4g", None),
    "sdongle_change_sequence_number": RegisterLocation(sdongle.SDongle, "change_sequence_number", None),
    "sdongle_connection_port": RegisterLocation(sdongle.Commands, "sdongle_connection_port", None),
    "sdongle_device_operation": RegisterLocation(sdongle.SDongle, "device_operation", None),
    "sdongle_device_operation_command": RegisterLocation(sdongle.SDongle, "device_operation_command", None),
    "sdongle_device_search_status": RegisterLocation(sdongle.SDongle, "device_search_status", None),
    "sdongle_grid_power": RegisterLocation(sdongle.SDongle, "grid_power", None),
    "sdongle_imei_4g": RegisterLocation(sdongle.SDongle, "imei_4g", None),
    "sdongle_load_power": RegisterLocation(sdongle.SDongle, "load_power", None),
    "sdongle_maximum_devices_allowed": RegisterLocation(sdongle.SDongle, "maximum_devices_allowed", None),
    "sdongle_monthly_remaining_traffic_4g": RegisterLocation(sdongle.SDongle, "monthly_remaining_traffic_4g", None),
    "sdongle_monthly_used_traffic_4g": RegisterLocation(sdongle.SDongle, "monthly_used_traffic_4g", None),
    "sdongle_monthly_used_traffic_correction_4g": RegisterLocation(
        sdongle.SDongle, "monthly_used_traffic_correction_4g", None
    ),
    "sdongle_network_mode_4g": RegisterLocation(sdongle.SDongle, "network_mode_4g", None),
    "sdongle_nms_server": RegisterLocation(sdongle.SDongle, "nms_server", None),
    "sdongle_nms_server_port1": RegisterLocation(sdongle.SDongle, "nms_server_port1", None),
    "sdongle_nms_server_port2": RegisterLocation(sdongle.SDongle, "nms_server_port2", None),
    "sdongle_ntp_time_synchronization": RegisterLocation(sdongle.SDongle, "ntp_time_synchronization", None),
    "sdongle_port_mode": RegisterLocation(sdongle.SDongle, "port_mode", None),
    "sdongle_registration_status": RegisterLocation(sdongle.SDongle, "registration_status", None),
    "sdongle_reported_data_record_period": RegisterLocation(sdongle.SDongle, "reported_data_record_period", None),
    "sdongle_reset": RegisterLocation(sdongle.Commands, "sdongle_reset", None),
    "sdongle_signal_strength_4g": RegisterLocation(sdongle.SDongle, "signal_strength_4g", None),
    "sdongle_ssl_encryption": RegisterLocation(sdongle.SDongle, "ssl_encryption", None),
    "sdongle_start_device_search": RegisterLocation(sdongle.SDongle, "start_device_search", None),
    "sdongle_system_4g": RegisterLocation(sdongle.SDongle, "system_4g", None),
    "sdongle_tcp_heartbeat_period": RegisterLocation(sdongle.SDongle, "tcp_heartbeat_period", None),
    "sdongle_total_active_power": RegisterLocation(sdongle.SDongle, "total_active_power", None),
    "sdongle_total_battery_power": RegisterLocation(sdongle.SDongle, "total_battery_power", None),
    "sdongle_total_input_power": RegisterLocation(sdongle.SDongle, "total_input_power", None),
    "sdongle_traffic_package_4g": RegisterLocation(sdongle.SDongle, "traffic_package_4g", None),
    "sdongle_traffic_status_4g": RegisterLocation(sdongle.SDongle, "traffic_status_4g", None),
    "sdongle_type": RegisterLocation(sdongle.SDongle, "type", None),
    "sdongle_unsolicited_report_interval": RegisterLocation(sdongle.SDongle, "unsolicited_report_interval", None),
    "sdongle_wireless_route_access_signal_strength": RegisterLocation(
        sdongle.SDongle, "wireless_route_access_signal_strength", None
    ),
    "serial_number": RegisterLocation(shared.DeviceIdentity, "serial_number", None),
    "shutdown": RegisterLocation(sun2000.Commands, "shutdown", None),
    "shutdown_time": RegisterLocation(sun2000.Inverter, "shutdown_time", None),
    "slave_dsp_version": RegisterLocation(sun2000.ProductInfo, "slave_dsp_version", None),
    "smartlogger_a_b_line_voltage_of_grid": RegisterLocation(smartlogger.SmartLogger, "a_b_line_voltage_of_grid", None),
    "smartlogger_active_alarm_sequence_number": RegisterLocation(
        smartlogger.SmartLogger, "active_alarm_sequence_number", None
    ),
    "smartlogger_active_ess_power": RegisterLocation(smartlogger.SmartLogger, "active_ess_power", None),
    "smartlogger_active_ess_power_adjustment_in_fixed_value": RegisterLocation(
        smartlogger.SmartLogger, "active_ess_power_adjustment_in_fixed_value", None
    ),
    "smartlogger_active_ess_power_adjustment_in_percentage": RegisterLocation(
        smartlogger.SmartLogger, "active_ess_power_adjustment_in_percentage", None
    ),
    "smartlogger_active_power": RegisterLocation(smartlogger.SmartLogger, "active_power", None),
    "smartlogger_active_power_adjustment": RegisterLocation(smartlogger.SmartLogger, "active_power_adjustment", None),
    "smartlogger_active_power_adjustment_highest_priority": RegisterLocation(
        smartlogger.SmartLogger, "active_power_adjustment_highest_priority", None
    ),
    "smartlogger_active_power_adjustment_in_percentage": RegisterLocation(
        smartlogger.SmartLogger, "active_power_adjustment_in_percentage", None
    ),
    "smartlogger_active_power_adjustment_target": RegisterLocation(
        smartlogger.SmartLogger, "active_power_adjustment_target", None
    ),
    "smartlogger_active_power_control_mode": RegisterLocation(
        smartlogger.SmartLogger, "active_power_control_mode", None
    ),
    "smartlogger_active_power_control_mode_plant": RegisterLocation(
        smartlogger.SmartLogger, "active_power_control_mode_plant", None
    ),
    "smartlogger_active_power_scheduling_in_percentage": RegisterLocation(
        smartlogger.SmartLogger, "active_power_scheduling_in_percentage", None
    ),
    "smartlogger_active_power_scheduling_target_value": RegisterLocation(
        smartlogger.SmartLogger, "active_power_scheduling_target_value", None
    ),
    "smartlogger_active_pv_power": RegisterLocation(smartlogger.SmartLogger, "active_pv_power", None),
    "smartlogger_active_pv_power_adjustment_in_fixed_value": RegisterLocation(
        smartlogger.SmartLogger, "active_pv_power_adjustment_in_fixed_value", None
    ),
    "smartlogger_active_pv_power_adjustment_in_percentage": RegisterLocation(
        smartlogger.SmartLogger, "active_pv_power_adjustment_in_percentage", None
    ),
    "smartlogger_alarm_1": RegisterLocation(smartlogger.SmartLoggerAlarms, "alarm_1", None),
    "smartlogger_alarm_2": RegisterLocation(smartlogger.SmartLoggerAlarms, "alarm_2", None),
    "smartlogger_alarm_3": RegisterLocation(smartlogger.SmartLoggerAlarms, "alarm_3", None),
    "smartlogger_alarm_4": RegisterLocation(smartlogger.SmartLoggerAlarms, "alarm_4", None),
    "smartlogger_alarm_5": RegisterLocation(smartlogger.SmartLoggerAlarms, "alarm_5", None),
    "smartlogger_alarm_6": RegisterLocation(smartlogger.SmartLoggerAlarms, "alarm_6", None),
    "smartlogger_alarm_7": RegisterLocation(smartlogger.SmartLoggerAlarms, "alarm_7", None),
    "smartlogger_array_black_start": RegisterLocation(smartlogger.SmartLogger, "array_black_start", None),
    "smartlogger_array_black_start_status": RegisterLocation(smartlogger.SmartLogger, "array_black_start_status", None),
    "smartlogger_array_in_operation": RegisterLocation(smartlogger.SmartLogger, "array_in_operation", None),
    "smartlogger_array_reset": RegisterLocation(smartlogger.SmartLogger, "array_reset", None),
    "smartlogger_array_shut_down": RegisterLocation(smartlogger.SmartLogger, "array_shut_down", None),
    "smartlogger_b_c_line_voltage_of_grid": RegisterLocation(smartlogger.SmartLogger, "b_c_line_voltage_of_grid", None),
    "smartlogger_c_a_line_voltage_of_grid": RegisterLocation(smartlogger.SmartLogger, "c_a_line_voltage_of_grid", None),
    "smartlogger_chargeable_capacity": RegisterLocation(smartlogger.SmartLogger, "chargeable_capacity", None),
    "smartlogger_city": RegisterLocation(smartlogger.SmartLogger, "city", None),
    "smartlogger_co2_emission_reduction_coefficient": RegisterLocation(
        smartlogger.SmartLogger, "co2_emission_reduction_coefficient", None
    ),
    "smartlogger_co2_reduced": RegisterLocation(smartlogger.SmartLogger, "co2_reduced", None),
    "smartlogger_co2_reduced_total": RegisterLocation(smartlogger.SmartLogger, "co2_reduced_total", None),
    "smartlogger_communication_status": RegisterLocation(smartlogger.SmartLogger, "communication_status", None),
    "smartlogger_conversion_coefficient": RegisterLocation(smartlogger.SmartLogger, "conversion_coefficient", None),
    "smartlogger_current_error_during_scanning": RegisterLocation(
        smartlogger.SmartLogger, "current_error_during_scanning", None
    ),
    "smartlogger_date_time": RegisterLocation(smartlogger.SmartLogger, "date_time", None),
    "smartlogger_daylight_saving_time_dst": RegisterLocation(smartlogger.SmartLogger, "daylight_saving_time_dst", None),
    "smartlogger_dc_current": RegisterLocation(smartlogger.SmartLogger, "dc_current", None),
    "smartlogger_dc_current_2": RegisterLocation(smartlogger.SmartLogger, "dc_current_2", None),
    "smartlogger_device_access_status": RegisterLocation(smartlogger.SmartLogger, "device_access_status", None),
    "smartlogger_device_connection_status": RegisterLocation(smartlogger.SmartLogger, "device_connection_status", None),
    "smartlogger_device_list_change": RegisterLocation(smartlogger.SmartLogger, "device_list_change", None),
    "smartlogger_device_name": RegisterLocation(smartlogger.SmartLogger, "device_name", None),
    "smartlogger_device_operation": RegisterLocation(smartlogger.SmartLogger, "device_operation", None),
    "smartlogger_di_group_state": RegisterLocation(smartlogger.SmartLogger, "di_group_state", None),
    "smartlogger_dischargeable_capacity": RegisterLocation(smartlogger.SmartLogger, "dischargeable_capacity", None),
    "smartlogger_dst_offset": RegisterLocation(smartlogger.SmartLogger, "dst_offset", None),
    "smartlogger_dst_state": RegisterLocation(smartlogger.SmartLogger, "dst_state", None),
    "smartlogger_energy_charged_today": RegisterLocation(smartlogger.SmartLogger, "energy_charged_today", None),
    "smartlogger_energy_discharged_today": RegisterLocation(smartlogger.SmartLogger, "energy_discharged_today", None),
    "smartlogger_equipment_serial_number_esn": RegisterLocation(
        smartlogger.SmartLogger, "equipment_serial_number_esn", None
    ),
    "smartlogger_ess_end_of_charge_soc": RegisterLocation(smartlogger.SmartLogger, "ess_end_of_charge_soc", None),
    "smartlogger_ess_end_of_discharge_soc": RegisterLocation(smartlogger.SmartLogger, "ess_end_of_discharge_soc", None),
    "smartlogger_ess_pcs_in_operation": RegisterLocation(smartlogger.SmartLogger, "ess_pcs_in_operation", None),
    "smartlogger_ess_pcs_shut_down": RegisterLocation(smartlogger.SmartLogger, "ess_pcs_shut_down", None),
    "smartlogger_ess_shutdown": RegisterLocation(smartlogger.SmartLogger, "ess_shutdown", None),
    "smartlogger_ess_startup": RegisterLocation(smartlogger.SmartLogger, "ess_startup", None),
    "smartlogger_external_meter_a_b_line_voltage": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter, "external_meter_a_b_line_voltage", None
    ),
    "smartlogger_external_meter_active_electricity": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter, "external_meter_active_electricity", None
    ),
    "smartlogger_external_meter_active_power": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter, "external_meter_active_power", None
    ),
    "smartlogger_external_meter_apparent_power": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter, "external_meter_apparent_power", None
    ),
    "smartlogger_external_meter_b_c_line_voltage": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter, "external_meter_b_c_line_voltage", None
    ),
    "smartlogger_external_meter_c_a_line_voltage": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter, "external_meter_c_a_line_voltage", None
    ),
    "smartlogger_external_meter_custom_1": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter, "external_meter_custom_1", None
    ),
    "smartlogger_external_meter_custom_10": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter, "external_meter_custom_10", None
    ),
    "smartlogger_external_meter_custom_2": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter, "external_meter_custom_2", None
    ),
    "smartlogger_external_meter_custom_3": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter, "external_meter_custom_3", None
    ),
    "smartlogger_external_meter_custom_4": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter, "external_meter_custom_4", None
    ),
    "smartlogger_external_meter_custom_5": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter, "external_meter_custom_5", None
    ),
    "smartlogger_external_meter_custom_6": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter, "external_meter_custom_6", None
    ),
    "smartlogger_external_meter_custom_7": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter, "external_meter_custom_7", None
    ),
    "smartlogger_external_meter_custom_8": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter, "external_meter_custom_8", None
    ),
    "smartlogger_external_meter_custom_9": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter, "external_meter_custom_9", None
    ),
    "smartlogger_external_meter_electricity_in_negative_active_electricity_price_segment_1": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter,
        "external_meter_electricity_in_negative_active_electricity_price_segment_1",
        None,
    ),
    "smartlogger_external_meter_electricity_in_negative_active_electricity_price_segment_2": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter,
        "external_meter_electricity_in_negative_active_electricity_price_segment_2",
        None,
    ),
    "smartlogger_external_meter_electricity_in_negative_active_electricity_price_segment_3": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter,
        "external_meter_electricity_in_negative_active_electricity_price_segment_3",
        None,
    ),
    "smartlogger_external_meter_electricity_in_negative_active_electricity_price_segment_4": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter,
        "external_meter_electricity_in_negative_active_electricity_price_segment_4",
        None,
    ),
    "smartlogger_external_meter_electricity_in_positive_active_electricity_price_segment_1": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter,
        "external_meter_electricity_in_positive_active_electricity_price_segment_1",
        None,
    ),
    "smartlogger_external_meter_electricity_in_positive_active_electricity_price_segment_2": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter,
        "external_meter_electricity_in_positive_active_electricity_price_segment_2",
        None,
    ),
    "smartlogger_external_meter_electricity_in_positive_active_electricity_price_segment_3": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter,
        "external_meter_electricity_in_positive_active_electricity_price_segment_3",
        None,
    ),
    "smartlogger_external_meter_electricity_in_positive_active_electricity_price_segment_4": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter,
        "external_meter_electricity_in_positive_active_electricity_price_segment_4",
        None,
    ),
    "smartlogger_external_meter_negative_active_electricity": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter, "external_meter_negative_active_electricity", None
    ),
    "smartlogger_external_meter_negative_reactive_electricity": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter, "external_meter_negative_reactive_electricity", None
    ),
    "smartlogger_external_meter_phase_a_active_power": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter, "external_meter_phase_a_active_power", None
    ),
    "smartlogger_external_meter_phase_a_current": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter, "external_meter_phase_a_current", None
    ),
    "smartlogger_external_meter_phase_a_voltage": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter, "external_meter_phase_a_voltage", None
    ),
    "smartlogger_external_meter_phase_b_active_power": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter, "external_meter_phase_b_active_power", None
    ),
    "smartlogger_external_meter_phase_b_current": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter, "external_meter_phase_b_current", None
    ),
    "smartlogger_external_meter_phase_b_voltage": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter, "external_meter_phase_b_voltage", None
    ),
    "smartlogger_external_meter_phase_c_active_power": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter, "external_meter_phase_c_active_power", None
    ),
    "smartlogger_external_meter_phase_c_current": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter, "external_meter_phase_c_current", None
    ),
    "smartlogger_external_meter_phase_c_voltage": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter, "external_meter_phase_c_voltage", None
    ),
    "smartlogger_external_meter_positive_active_electricity": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter, "external_meter_positive_active_electricity", None
    ),
    "smartlogger_external_meter_positive_active_electricity_total": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter, "external_meter_positive_active_electricity_total", None
    ),
    "smartlogger_external_meter_positive_reactive_electricity": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter, "external_meter_positive_reactive_electricity", None
    ),
    "smartlogger_external_meter_positive_reactive_electricity_total": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter, "external_meter_positive_reactive_electricity_total", None
    ),
    "smartlogger_external_meter_power_factor": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter, "external_meter_power_factor", None
    ),
    "smartlogger_external_meter_reactive_electricity": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter, "external_meter_reactive_electricity", None
    ),
    "smartlogger_external_meter_reactive_power": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter, "external_meter_reactive_power", None
    ),
    "smartlogger_external_meter_total_active_electricity": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter, "external_meter_total_active_electricity", None
    ),
    "smartlogger_external_meter_total_reactive_electricity": RegisterLocation(
        smartlogger.SmartLoggerExternalMeter, "external_meter_total_reactive_electricity", None
    ),
    "smartlogger_fast_device_access": RegisterLocation(smartlogger.SmartLogger, "fast_device_access", None),
    "smartlogger_frequency_adjustment_value_for_vsg_synchronous_control": RegisterLocation(
        smartlogger.SmartLogger, "frequency_adjustment_value_for_vsg_synchronous_control", None
    ),
    "smartlogger_highest_stable_charge_power_of_ess": RegisterLocation(
        smartlogger.SmartLogger, "highest_stable_charge_power_of_ess", None
    ),
    "smartlogger_highest_stable_discharge_power_of_ess": RegisterLocation(
        smartlogger.SmartLogger, "highest_stable_discharge_power_of_ess", None
    ),
    "smartlogger_historical_alarm_sequence_number": RegisterLocation(
        smartlogger.SmartLogger, "historical_alarm_sequence_number", None
    ),
    "smartlogger_i_v_curve_scanning": RegisterLocation(smartlogger.SmartLogger, "i_v_curve_scanning", None),
    "smartlogger_input_power": RegisterLocation(smartlogger.SmartLogger, "input_power", None),
    "smartlogger_inspection_control": RegisterLocation(smartlogger.SmartLogger, "inspection_control", None),
    "smartlogger_inverter_efficiency": RegisterLocation(smartlogger.SmartLogger, "inverter_efficiency", None),
    "smartlogger_local_time": RegisterLocation(smartlogger.SmartLogger, "local_time", None),
    "smartlogger_locking_status": RegisterLocation(smartlogger.SmartLogger, "locking_status", None),
    "smartlogger_maximum_active_power_adjustment_value": RegisterLocation(
        smartlogger.SmartLogger, "maximum_active_power_adjustment_value", None
    ),
    "smartlogger_maximum_active_pv_power_adjustment_value": RegisterLocation(
        smartlogger.SmartLogger, "maximum_active_pv_power_adjustment_value", None
    ),
    "smartlogger_maximum_ess_charge_power": RegisterLocation(smartlogger.SmartLogger, "maximum_ess_charge_power", None),
    "smartlogger_maximum_ess_discharge_power": RegisterLocation(
        smartlogger.SmartLogger, "maximum_ess_discharge_power", None
    ),
    "smartlogger_maximum_reactive_ess_power_adjustment_value": RegisterLocation(
        smartlogger.SmartLogger, "maximum_reactive_ess_power_adjustment_value", None
    ),
    "smartlogger_maximum_reactive_power_adjustment_value": RegisterLocation(
        smartlogger.SmartLogger, "maximum_reactive_power_adjustment_value", None
    ),
    "smartlogger_maximum_reactive_pv_power_adjustment_value": RegisterLocation(
        smartlogger.SmartLogger, "maximum_reactive_pv_power_adjustment_value", None
    ),
    "smartlogger_minimum_active_power_adjustment_value": RegisterLocation(
        smartlogger.SmartLogger, "minimum_active_power_adjustment_value", None
    ),
    "smartlogger_minimum_reactive_ess_power_adjustment_value": RegisterLocation(
        smartlogger.SmartLogger, "minimum_reactive_ess_power_adjustment_value", None
    ),
    "smartlogger_minimum_reactive_power_adjustment_value": RegisterLocation(
        smartlogger.SmartLogger, "minimum_reactive_power_adjustment_value", None
    ),
    "smartlogger_minimum_reactive_pv_power_adjustment_value": RegisterLocation(
        smartlogger.SmartLogger, "minimum_reactive_pv_power_adjustment_value", None
    ),
    "smartlogger_phase_a_current_of_grid": RegisterLocation(smartlogger.SmartLogger, "phase_a_current_of_grid", None),
    "smartlogger_phase_b_current_of_grid": RegisterLocation(smartlogger.SmartLogger, "phase_b_current_of_grid", None),
    "smartlogger_phase_c_current_of_grid": RegisterLocation(smartlogger.SmartLogger, "phase_c_current_of_grid", None),
    "smartlogger_plant_status": RegisterLocation(smartlogger.SmartLogger, "plant_status", None),
    "smartlogger_plant_status_gansu": RegisterLocation(smartlogger.SmartLogger, "plant_status_gansu", None),
    "smartlogger_plant_status_ningxia": RegisterLocation(smartlogger.SmartLogger, "plant_status_ningxia", None),
    "smartlogger_plant_status_qinghai": RegisterLocation(smartlogger.SmartLogger, "plant_status_qinghai", None),
    "smartlogger_plant_status_shaanxi": RegisterLocation(smartlogger.SmartLogger, "plant_status_shaanxi", None),
    "smartlogger_power_factor": RegisterLocation(smartlogger.SmartLogger, "power_factor", None),
    "smartlogger_power_factor_adjustment": RegisterLocation(smartlogger.SmartLogger, "power_factor_adjustment", None),
    "smartlogger_power_on_the_pcs_of_the_subarray": RegisterLocation(
        smartlogger.SmartLogger, "power_on_the_pcs_of_the_subarray", None
    ),
    "smartlogger_power_supply_from_grid_today": RegisterLocation(
        smartlogger.SmartLogger, "power_supply_from_grid_today", None
    ),
    "smartlogger_pv_array_pcs_working_mode": RegisterLocation(
        smartlogger.SmartLogger, "pv_array_pcs_working_mode", None
    ),
    "smartlogger_pv_inverter_in_operation": RegisterLocation(smartlogger.SmartLogger, "pv_inverter_in_operation", None),
    "smartlogger_pv_inverter_shut_down": RegisterLocation(smartlogger.SmartLogger, "pv_inverter_shut_down", None),
    "smartlogger_pv_inverter_shutdown": RegisterLocation(smartlogger.SmartLogger, "pv_inverter_shutdown", None),
    "smartlogger_pv_inverter_startup": RegisterLocation(smartlogger.SmartLogger, "pv_inverter_startup", None),
    "smartlogger_pv_module_capacity": RegisterLocation(smartlogger.SmartLogger, "pv_module_capacity", None),
    "smartlogger_quantity_of_running_ess_pcss": RegisterLocation(
        smartlogger.SmartLogger, "quantity_of_running_ess_pcss", None
    ),
    "smartlogger_quantity_of_running_pv_inverters": RegisterLocation(
        smartlogger.SmartLogger, "quantity_of_running_pv_inverters", None
    ),
    "smartlogger_rated_ess_capacity": RegisterLocation(smartlogger.SmartLogger, "rated_ess_capacity", None),
    "smartlogger_rated_ess_capacity_in_ah": RegisterLocation(smartlogger.SmartLogger, "rated_ess_capacity_in_ah", None),
    "smartlogger_rated_ess_power": RegisterLocation(smartlogger.SmartLogger, "rated_ess_power", None),
    "smartlogger_rated_plant_capacity": RegisterLocation(smartlogger.SmartLogger, "rated_plant_capacity", None),
    "smartlogger_rated_pv_power": RegisterLocation(smartlogger.SmartLogger, "rated_pv_power", None),
    "smartlogger_reactive_ess_power": RegisterLocation(smartlogger.SmartLogger, "reactive_ess_power", None),
    "smartlogger_reactive_ess_power_adjustment_in_fixed_value": RegisterLocation(
        smartlogger.SmartLogger, "reactive_ess_power_adjustment_in_fixed_value", None
    ),
    "smartlogger_reactive_power": RegisterLocation(smartlogger.SmartLogger, "reactive_power", None),
    "smartlogger_reactive_power_adjustment": RegisterLocation(
        smartlogger.SmartLogger, "reactive_power_adjustment", None
    ),
    "smartlogger_reactive_power_adjustment_highest_priority": RegisterLocation(
        smartlogger.SmartLogger, "reactive_power_adjustment_highest_priority", None
    ),
    "smartlogger_reactive_power_adjustment_target": RegisterLocation(
        smartlogger.SmartLogger, "reactive_power_adjustment_target", None
    ),
    "smartlogger_reactive_power_control_mode": RegisterLocation(
        smartlogger.SmartLogger, "reactive_power_control_mode", None
    ),
    "smartlogger_reactive_power_control_mode_subarray": RegisterLocation(
        smartlogger.SmartLogger, "reactive_power_control_mode_subarray", None
    ),
    "smartlogger_reactive_power_scheduling_curve_mode": RegisterLocation(
        smartlogger.SmartLogger, "reactive_power_scheduling_curve_mode", None
    ),
    "smartlogger_reactive_power_scheduling_target_value": RegisterLocation(
        smartlogger.SmartLogger, "reactive_power_scheduling_target_value", None
    ),
    "smartlogger_reactive_pv_power": RegisterLocation(smartlogger.SmartLogger, "reactive_pv_power", None),
    "smartlogger_reactive_pv_power_adjustment_in_fixed_value": RegisterLocation(
        smartlogger.SmartLogger, "reactive_pv_power_adjustment_in_fixed_value", None
    ),
    "smartlogger_reserved": RegisterLocation(smartlogger.SmartLogger, "reserved", None),
    "smartlogger_shut_down_array_upon_communication_timeout": RegisterLocation(
        smartlogger.SmartLogger, "shut_down_array_upon_communication_timeout", None
    ),
    "smartlogger_shut_down_the_pcs_of_the_subarray": RegisterLocation(
        smartlogger.SmartLogger, "shut_down_the_pcs_of_the_subarray", None
    ),
    "smartlogger_shutdown": RegisterLocation(smartlogger.SmartLogger, "shutdown", None),
    "smartlogger_soc": RegisterLocation(smartlogger.SmartLogger, "soc", None),
    "smartlogger_soe": RegisterLocation(smartlogger.SmartLogger, "soe", None),
    "smartlogger_soh": RegisterLocation(smartlogger.SmartLogger, "soh", None),
    "smartlogger_start_up_array_upon_communication_recovery": RegisterLocation(
        smartlogger.SmartLogger, "start_up_array_upon_communication_recovery", None
    ),
    "smartlogger_startup": RegisterLocation(smartlogger.SmartLogger, "startup", None),
    "smartlogger_startup_shutdown": RegisterLocation(smartlogger.SmartLogger, "startup_shutdown", None),
    "smartlogger_startup_shutdown_ess": RegisterLocation(smartlogger.SmartLogger, "startup_shutdown_ess", None),
    "smartlogger_status_information": RegisterLocation(smartlogger.SmartLogger, "status_information", None),
    "smartlogger_subarray_pv_inverter_microgrid_adaptability": RegisterLocation(
        smartlogger.SmartLogger, "subarray_pv_inverter_microgrid_adaptability", None
    ),
    "smartlogger_system_reset": RegisterLocation(smartlogger.SmartLogger, "system_reset", None),
    "smartlogger_system_time_day": RegisterLocation(smartlogger.SmartLogger, "system_time_day", None),
    "smartlogger_system_time_hour": RegisterLocation(smartlogger.SmartLogger, "system_time_hour", None),
    "smartlogger_system_time_minute": RegisterLocation(smartlogger.SmartLogger, "system_time_minute", None),
    "smartlogger_system_time_month": RegisterLocation(smartlogger.SmartLogger, "system_time_month", None),
    "smartlogger_system_time_second": RegisterLocation(smartlogger.SmartLogger, "system_time_second", None),
    "smartlogger_system_time_year": RegisterLocation(smartlogger.SmartLogger, "system_time_year", None),
    "smartlogger_the_active_power_gradient_register": RegisterLocation(
        smartlogger.SmartLogger, "the_active_power_gradient_register", None
    ),
    "smartlogger_time_for_communication_exception_detection": RegisterLocation(
        smartlogger.SmartLogger, "time_for_communication_exception_detection", None
    ),
    "smartlogger_time_zone": RegisterLocation(smartlogger.SmartLogger, "time_zone", None),
    "smartlogger_todays_power_generation_hours": RegisterLocation(
        smartlogger.SmartLogger, "todays_power_generation_hours", None
    ),
    "smartlogger_total_energy_charged": RegisterLocation(smartlogger.SmartLogger, "total_energy_charged", None),
    "smartlogger_total_energy_discharge_d": RegisterLocation(smartlogger.SmartLogger, "total_energy_discharge_d", None),
    "smartlogger_total_energy_yield": RegisterLocation(smartlogger.SmartLogger, "total_energy_yield", None),
    "smartlogger_total_power_supply_from_grid": RegisterLocation(
        smartlogger.SmartLogger, "total_power_supply_from_grid", None
    ),
    "smartlogger_total_rated_capacity_of_grid_tied_inverters": RegisterLocation(
        smartlogger.SmartLogger, "total_rated_capacity_of_grid_tied_inverters", None
    ),
    "smartlogger_transfer_trip": RegisterLocation(smartlogger.SmartLogger, "transfer_trip", None),
    "smartlogger_voltage_adjustment_value_for_vsg_synchronous_control": RegisterLocation(
        smartlogger.SmartLogger, "voltage_adjustment_value_for_vsg_synchronous_control", None
    ),
    "smartlogger_working_mode": RegisterLocation(smartlogger.SmartLogger, "working_mode", None),
    "smartlogger_yield_today": RegisterLocation(smartlogger.SmartLogger, "yield_today", None),
    "software_version": RegisterLocation(shared.DeviceIdentity, "software_version", None),
    "startup": RegisterLocation(sun2000.Commands, "startup", None),
    "startup_time": RegisterLocation(sun2000.Inverter, "startup_time", None),
    "state_1": RegisterLocation(sun2000.Inverter, "state_1", None),
    "state_2": RegisterLocation(sun2000.Inverter, "state_2", None),
    "state_3": RegisterLocation(sun2000.Inverter, "state_3", None),
    "state_of_capacity": RegisterLocation(emma.Emma, "state_of_capacity", None),
    "storage_backup_power_state_of_charge": RegisterLocation(
        sun2000.StorageSettings, "storage_backup_power_state_of_charge", None
    ),
    "storage_bus_current": RegisterLocation(sun2000.StorageSettings, "storage_bus_current", None),
    "storage_bus_voltage": RegisterLocation(sun2000.StorageSettings, "storage_bus_voltage", None),
    "storage_capacity_control_mode": RegisterLocation(sun2000.StorageSettings, "storage_capacity_control_mode", None),
    "storage_capacity_control_periods": RegisterLocation(
        sun2000.StorageSettings, "storage_capacity_control_periods", None
    ),
    "storage_capacity_control_soc_peak_shaving": RegisterLocation(
        sun2000.StorageSettings, "storage_capacity_control_soc_peak_shaving", None
    ),
    "storage_charge_discharge_power": RegisterLocation(sun2000.StorageSettings, "storage_charge_discharge_power", None),
    "storage_charge_from_grid_function": RegisterLocation(
        sun2000.StorageSettings, "storage_charge_from_grid_function", None
    ),
    "storage_charging_cutoff_capacity": RegisterLocation(
        sun2000.StorageSettings, "storage_charging_cutoff_capacity", None
    ),
    "storage_current_day_charge_capacity": RegisterLocation(
        sun2000.StorageSettings, "storage_current_day_charge_capacity", None
    ),
    "storage_current_day_discharge_capacity": RegisterLocation(
        sun2000.StorageSettings, "storage_current_day_discharge_capacity", None
    ),
    "storage_discharging_cutoff_capacity": RegisterLocation(
        sun2000.StorageSettings, "storage_discharging_cutoff_capacity", None
    ),
    "storage_excess_pv_energy_use_in_tou": RegisterLocation(
        sun2000.StorageSettings, "storage_excess_pv_energy_use_in_tou", None
    ),
    "storage_fixed_charging_and_discharging_periods": RegisterLocation(
        sun2000.StorageSettings, "storage_fixed_charging_and_discharging_periods", None
    ),
    "storage_forced_charging_and_discharging_period": RegisterLocation(
        sun2000.StorageSettings, "storage_forced_charging_and_discharging_period", None
    ),
    "storage_forced_charging_and_discharging_power": RegisterLocation(
        sun2000.StorageSettings, "storage_forced_charging_and_discharging_power", None
    ),
    "storage_forcible_charge_discharge_setting_mode": RegisterLocation(
        sun2000.StorageSettings, "storage_forcible_charge_discharge_setting_mode", None
    ),
    "storage_forcible_charge_discharge_soc": RegisterLocation(
        sun2000.StorageSettings, "storage_forcible_charge_discharge_soc", None
    ),
    "storage_forcible_charge_power": RegisterLocation(sun2000.StorageSettings, "storage_forcible_charge_power", None),
    "storage_forcible_discharge_power": RegisterLocation(
        sun2000.StorageSettings, "storage_forcible_discharge_power", None
    ),
    "storage_grid_charge_cutoff_state_of_charge": RegisterLocation(
        sun2000.StorageSettings, "storage_grid_charge_cutoff_state_of_charge", None
    ),
    "storage_huawei_luna2000_time_of_use_charging_and_discharging_periods": RegisterLocation(
        sun2000.StorageSettings, "storage_huawei_luna2000_time_of_use_charging_and_discharging_periods", None
    ),
    "storage_lcoe": RegisterLocation(sun2000.StorageSettings, "storage_lcoe", None),
    "storage_lg_resu_time_of_use_price_periods": RegisterLocation(
        sun2000.StorageSettings, "storage_lg_resu_time_of_use_price_periods", None
    ),
    "storage_maximum_charge_power": RegisterLocation(sun2000.StorageSettings, "storage_maximum_charge_power", None),
    "storage_maximum_charging_power": RegisterLocation(sun2000.StorageSettings, "storage_maximum_charging_power", None),
    "storage_maximum_discharge_power": RegisterLocation(
        sun2000.StorageSettings, "storage_maximum_discharge_power", None
    ),
    "storage_maximum_discharging_power": RegisterLocation(
        sun2000.StorageSettings, "storage_maximum_discharging_power", None
    ),
    "storage_maximum_power_of_charge_from_grid": RegisterLocation(
        sun2000.StorageSettings, "storage_maximum_power_of_charge_from_grid", None
    ),
    "storage_power_limit_grid_tied_point": RegisterLocation(
        sun2000.StorageSettings, "storage_power_limit_grid_tied_point", None
    ),
    "storage_power_of_charge_from_grid": RegisterLocation(
        sun2000.StorageSettings, "storage_power_of_charge_from_grid", None
    ),
    "storage_rated_capacity": RegisterLocation(sun2000.StorageSettings, "storage_rated_capacity", None),
    "storage_running_status": RegisterLocation(sun2000.StorageSettings, "storage_running_status", None),
    "storage_state_of_capacity": RegisterLocation(sun2000.StorageSettings, "storage_state_of_capacity", None),
    "storage_time_of_use_price": RegisterLocation(sun2000.StorageSettings, "storage_time_of_use_price", None),
    "storage_total_charge": RegisterLocation(sun2000.StorageSettings, "storage_total_charge", None),
    "storage_total_discharge": RegisterLocation(sun2000.StorageSettings, "storage_total_discharge", None),
    "storage_unit_1_battery_pack_1_charge_discharge_power": RegisterLocation(
        sun2000.BatteryPack, "charge_discharge_power", 1
    ),
    "storage_unit_1_battery_pack_1_current": RegisterLocation(sun2000.BatteryPack, "current", 1),
    "storage_unit_1_battery_pack_1_firmware_version": RegisterLocation(sun2000.BatteryPack, "firmware_version", 1),
    "storage_unit_1_battery_pack_1_maximum_temperature": RegisterLocation(
        sun2000.BatteryPack, "maximum_temperature", 1
    ),
    "storage_unit_1_battery_pack_1_minimum_temperature": RegisterLocation(
        sun2000.BatteryPack, "minimum_temperature", 1
    ),
    "storage_unit_1_battery_pack_1_serial_number": RegisterLocation(sun2000.BatteryPack, "serial_number", 1),
    "storage_unit_1_battery_pack_1_soh_calibration_status": RegisterLocation(
        sun2000.BatteryPack, "soh_calibration_status", 1
    ),
    "storage_unit_1_battery_pack_1_state_of_capacity": RegisterLocation(sun2000.BatteryPack, "state_of_capacity", 1),
    "storage_unit_1_battery_pack_1_total_charge": RegisterLocation(sun2000.BatteryPack, "total_charge", 1),
    "storage_unit_1_battery_pack_1_total_discharge": RegisterLocation(sun2000.BatteryPack, "total_discharge", 1),
    "storage_unit_1_battery_pack_1_voltage": RegisterLocation(sun2000.BatteryPack, "voltage", 1),
    "storage_unit_1_battery_pack_1_working_status": RegisterLocation(sun2000.BatteryPack, "working_status", 1),
    "storage_unit_1_battery_pack_2_charge_discharge_power": RegisterLocation(
        sun2000.BatteryPack, "charge_discharge_power", 2
    ),
    "storage_unit_1_battery_pack_2_current": RegisterLocation(sun2000.BatteryPack, "current", 2),
    "storage_unit_1_battery_pack_2_firmware_version": RegisterLocation(sun2000.BatteryPack, "firmware_version", 2),
    "storage_unit_1_battery_pack_2_maximum_temperature": RegisterLocation(
        sun2000.BatteryPack, "maximum_temperature", 2
    ),
    "storage_unit_1_battery_pack_2_minimum_temperature": RegisterLocation(
        sun2000.BatteryPack, "minimum_temperature", 2
    ),
    "storage_unit_1_battery_pack_2_serial_number": RegisterLocation(sun2000.BatteryPack, "serial_number", 2),
    "storage_unit_1_battery_pack_2_soh_calibration_status": RegisterLocation(
        sun2000.BatteryPack, "soh_calibration_status", 2
    ),
    "storage_unit_1_battery_pack_2_state_of_capacity": RegisterLocation(sun2000.BatteryPack, "state_of_capacity", 2),
    "storage_unit_1_battery_pack_2_total_charge": RegisterLocation(sun2000.BatteryPack, "total_charge", 2),
    "storage_unit_1_battery_pack_2_total_discharge": RegisterLocation(sun2000.BatteryPack, "total_discharge", 2),
    "storage_unit_1_battery_pack_2_voltage": RegisterLocation(sun2000.BatteryPack, "voltage", 2),
    "storage_unit_1_battery_pack_2_working_status": RegisterLocation(sun2000.BatteryPack, "working_status", 2),
    "storage_unit_1_battery_pack_3_charge_discharge_power": RegisterLocation(
        sun2000.BatteryPack, "charge_discharge_power", 3
    ),
    "storage_unit_1_battery_pack_3_current": RegisterLocation(sun2000.BatteryPack, "current", 3),
    "storage_unit_1_battery_pack_3_firmware_version": RegisterLocation(sun2000.BatteryPack, "firmware_version", 3),
    "storage_unit_1_battery_pack_3_maximum_temperature": RegisterLocation(
        sun2000.BatteryPack, "maximum_temperature", 3
    ),
    "storage_unit_1_battery_pack_3_minimum_temperature": RegisterLocation(
        sun2000.BatteryPack, "minimum_temperature", 3
    ),
    "storage_unit_1_battery_pack_3_serial_number": RegisterLocation(sun2000.BatteryPack, "serial_number", 3),
    "storage_unit_1_battery_pack_3_soh_calibration_status": RegisterLocation(
        sun2000.BatteryPack, "soh_calibration_status", 3
    ),
    "storage_unit_1_battery_pack_3_state_of_capacity": RegisterLocation(sun2000.BatteryPack, "state_of_capacity", 3),
    "storage_unit_1_battery_pack_3_total_charge": RegisterLocation(sun2000.BatteryPack, "total_charge", 3),
    "storage_unit_1_battery_pack_3_total_discharge": RegisterLocation(sun2000.BatteryPack, "total_discharge", 3),
    "storage_unit_1_battery_pack_3_voltage": RegisterLocation(sun2000.BatteryPack, "voltage", 3),
    "storage_unit_1_battery_pack_3_working_status": RegisterLocation(sun2000.BatteryPack, "working_status", 3),
    "storage_unit_1_battery_temperature": RegisterLocation(sun2000.StorageUnit, "battery_temperature", 1),
    "storage_unit_1_bms_version": RegisterLocation(sun2000.StorageUnit1Only, "bms_version", None),
    "storage_unit_1_bus_current": RegisterLocation(sun2000.StorageUnit, "bus_current", 1),
    "storage_unit_1_bus_voltage": RegisterLocation(sun2000.StorageUnit, "bus_voltage", 1),
    "storage_unit_1_charge_discharge_power": RegisterLocation(sun2000.StorageUnit, "charge_discharge_power", 1),
    "storage_unit_1_current_day_charge_capacity": RegisterLocation(
        sun2000.StorageUnit, "current_day_charge_capacity", 1
    ),
    "storage_unit_1_current_day_discharge_capacity": RegisterLocation(
        sun2000.StorageUnit, "current_day_discharge_capacity", 1
    ),
    "storage_unit_1_dcdc_version": RegisterLocation(sun2000.StorageUnit1Only, "dcdc_version", None),
    "storage_unit_1_fault_id": RegisterLocation(sun2000.StorageUnit1Only, "fault_id", None),
    "storage_unit_1_no": RegisterLocation(sun2000.StorageUnit, "no", 1),
    "storage_unit_1_pack_1_no": RegisterLocation(sun2000.StorageUnit, "pack_1_no", 1),
    "storage_unit_1_pack_2_no": RegisterLocation(sun2000.StorageUnit, "pack_2_no", 1),
    "storage_unit_1_pack_3_no": RegisterLocation(sun2000.StorageUnit, "pack_3_no", 1),
    "storage_unit_1_product_model": RegisterLocation(sun2000.StorageUnit, "product_model", 1),
    "storage_unit_1_rated_charge_power": RegisterLocation(sun2000.StorageUnit1Only, "rated_charge_power", None),
    "storage_unit_1_rated_discharge_power": RegisterLocation(sun2000.StorageUnit1Only, "rated_discharge_power", None),
    "storage_unit_1_remaining_charge_dis_charge_time": RegisterLocation(
        sun2000.StorageUnit1Only, "remaining_charge_dis_charge_time", None
    ),
    "storage_unit_1_running_status": RegisterLocation(sun2000.StorageUnit, "running_status", 1),
    "storage_unit_1_serial_number": RegisterLocation(sun2000.StorageUnit, "serial_number", 1),
    "storage_unit_1_software_version": RegisterLocation(sun2000.StorageUnit, "software_version", 1),
    "storage_unit_1_state_of_capacity": RegisterLocation(sun2000.StorageUnit, "state_of_capacity", 1),
    "storage_unit_1_total_charge": RegisterLocation(sun2000.StorageUnit, "total_charge", 1),
    "storage_unit_1_total_discharge": RegisterLocation(sun2000.StorageUnit, "total_discharge", 1),
    "storage_unit_1_working_mode_b": RegisterLocation(sun2000.StorageUnit1Only, "working_mode_b", None),
    "storage_unit_2_battery_pack_1_charge_discharge_power": RegisterLocation(
        sun2000.BatteryPack, "charge_discharge_power", 4
    ),
    "storage_unit_2_battery_pack_1_current": RegisterLocation(sun2000.BatteryPack, "current", 4),
    "storage_unit_2_battery_pack_1_firmware_version": RegisterLocation(sun2000.BatteryPack, "firmware_version", 4),
    "storage_unit_2_battery_pack_1_maximum_temperature": RegisterLocation(
        sun2000.BatteryPack, "maximum_temperature", 4
    ),
    "storage_unit_2_battery_pack_1_minimum_temperature": RegisterLocation(
        sun2000.BatteryPack, "minimum_temperature", 4
    ),
    "storage_unit_2_battery_pack_1_serial_number": RegisterLocation(sun2000.BatteryPack, "serial_number", 4),
    "storage_unit_2_battery_pack_1_soh_calibration_status": RegisterLocation(
        sun2000.BatteryPack, "soh_calibration_status", 4
    ),
    "storage_unit_2_battery_pack_1_state_of_capacity": RegisterLocation(sun2000.BatteryPack, "state_of_capacity", 4),
    "storage_unit_2_battery_pack_1_total_charge": RegisterLocation(sun2000.BatteryPack, "total_charge", 4),
    "storage_unit_2_battery_pack_1_total_discharge": RegisterLocation(sun2000.BatteryPack, "total_discharge", 4),
    "storage_unit_2_battery_pack_1_voltage": RegisterLocation(sun2000.BatteryPack, "voltage", 4),
    "storage_unit_2_battery_pack_1_working_status": RegisterLocation(sun2000.BatteryPack, "working_status", 4),
    "storage_unit_2_battery_pack_2_charge_discharge_power": RegisterLocation(
        sun2000.BatteryPack, "charge_discharge_power", 5
    ),
    "storage_unit_2_battery_pack_2_current": RegisterLocation(sun2000.BatteryPack, "current", 5),
    "storage_unit_2_battery_pack_2_firmware_version": RegisterLocation(sun2000.BatteryPack, "firmware_version", 5),
    "storage_unit_2_battery_pack_2_maximum_temperature": RegisterLocation(
        sun2000.BatteryPack, "maximum_temperature", 5
    ),
    "storage_unit_2_battery_pack_2_minimum_temperature": RegisterLocation(
        sun2000.BatteryPack, "minimum_temperature", 5
    ),
    "storage_unit_2_battery_pack_2_serial_number": RegisterLocation(sun2000.BatteryPack, "serial_number", 5),
    "storage_unit_2_battery_pack_2_soh_calibration_status": RegisterLocation(
        sun2000.BatteryPack, "soh_calibration_status", 5
    ),
    "storage_unit_2_battery_pack_2_state_of_capacity": RegisterLocation(sun2000.BatteryPack, "state_of_capacity", 5),
    "storage_unit_2_battery_pack_2_total_charge": RegisterLocation(sun2000.BatteryPack, "total_charge", 5),
    "storage_unit_2_battery_pack_2_total_discharge": RegisterLocation(sun2000.BatteryPack, "total_discharge", 5),
    "storage_unit_2_battery_pack_2_voltage": RegisterLocation(sun2000.BatteryPack, "voltage", 5),
    "storage_unit_2_battery_pack_2_working_status": RegisterLocation(sun2000.BatteryPack, "working_status", 5),
    "storage_unit_2_battery_pack_3_charge_discharge_power": RegisterLocation(
        sun2000.BatteryPack, "charge_discharge_power", 6
    ),
    "storage_unit_2_battery_pack_3_current": RegisterLocation(sun2000.BatteryPack, "current", 6),
    "storage_unit_2_battery_pack_3_firmware_version": RegisterLocation(sun2000.BatteryPack, "firmware_version", 6),
    "storage_unit_2_battery_pack_3_maximum_temperature": RegisterLocation(
        sun2000.BatteryPack, "maximum_temperature", 6
    ),
    "storage_unit_2_battery_pack_3_minimum_temperature": RegisterLocation(
        sun2000.BatteryPack, "minimum_temperature", 6
    ),
    "storage_unit_2_battery_pack_3_serial_number": RegisterLocation(sun2000.BatteryPack, "serial_number", 6),
    "storage_unit_2_battery_pack_3_soh_calibration_status": RegisterLocation(
        sun2000.BatteryPack, "soh_calibration_status", 6
    ),
    "storage_unit_2_battery_pack_3_state_of_capacity": RegisterLocation(sun2000.BatteryPack, "state_of_capacity", 6),
    "storage_unit_2_battery_pack_3_total_charge": RegisterLocation(sun2000.BatteryPack, "total_charge", 6),
    "storage_unit_2_battery_pack_3_total_discharge": RegisterLocation(sun2000.BatteryPack, "total_discharge", 6),
    "storage_unit_2_battery_pack_3_voltage": RegisterLocation(sun2000.BatteryPack, "voltage", 6),
    "storage_unit_2_battery_pack_3_working_status": RegisterLocation(sun2000.BatteryPack, "working_status", 6),
    "storage_unit_2_battery_temperature": RegisterLocation(sun2000.StorageUnit, "battery_temperature", 2),
    "storage_unit_2_bus_current": RegisterLocation(sun2000.StorageUnit, "bus_current", 2),
    "storage_unit_2_bus_voltage": RegisterLocation(sun2000.StorageUnit, "bus_voltage", 2),
    "storage_unit_2_charge_discharge_power": RegisterLocation(sun2000.StorageUnit, "charge_discharge_power", 2),
    "storage_unit_2_current_day_charge_capacity": RegisterLocation(
        sun2000.StorageUnit, "current_day_charge_capacity", 2
    ),
    "storage_unit_2_current_day_discharge_capacity": RegisterLocation(
        sun2000.StorageUnit, "current_day_discharge_capacity", 2
    ),
    "storage_unit_2_no": RegisterLocation(sun2000.StorageUnit, "no", 2),
    "storage_unit_2_pack_1_no": RegisterLocation(sun2000.StorageUnit, "pack_1_no", 2),
    "storage_unit_2_pack_2_no": RegisterLocation(sun2000.StorageUnit, "pack_2_no", 2),
    "storage_unit_2_pack_3_no": RegisterLocation(sun2000.StorageUnit, "pack_3_no", 2),
    "storage_unit_2_product_model": RegisterLocation(sun2000.StorageUnit, "product_model", 2),
    "storage_unit_2_running_status": RegisterLocation(sun2000.StorageUnit, "running_status", 2),
    "storage_unit_2_serial_number": RegisterLocation(sun2000.StorageUnit, "serial_number", 2),
    "storage_unit_2_software_version": RegisterLocation(sun2000.StorageUnit, "software_version", 2),
    "storage_unit_2_state_of_capacity": RegisterLocation(sun2000.StorageUnit, "state_of_capacity", 2),
    "storage_unit_2_total_charge": RegisterLocation(sun2000.StorageUnit, "total_charge", 2),
    "storage_unit_2_total_discharge": RegisterLocation(sun2000.StorageUnit, "total_discharge", 2),
    "storage_unit_soh_calibration_release_lower_limit_of_soc": RegisterLocation(
        sun2000.StorageSettings, "storage_unit_soh_calibration_release_lower_limit_of_soc", None
    ),
    "storage_unit_soh_calibration_status": RegisterLocation(
        sun2000.StorageSettings, "storage_unit_soh_calibration_status", None
    ),
    "storage_working_mode_a": RegisterLocation(sun2000.StorageSettings, "storage_working_mode_a", None),
    "storage_working_mode_settings": RegisterLocation(sun2000.StorageSettings, "storage_working_mode_settings", None),
    "subdevice_in_position_flag": RegisterLocation(sun2000.ProductInfo, "subdevice_in_position_flag", None),
    "subdevice_support_flag": RegisterLocation(sun2000.ProductInfo, "subdevice_support_flag", None),
    "supply_from_grid_today": RegisterLocation(emma.Emma, "supply_from_grid_today", None),
    "system_time": RegisterLocation(sun2000.Configuration, "system_time", None),
    "system_time_raw": RegisterLocation(sun2000.Configuration, "system_time_raw", None),
    "time_zone": RegisterLocation(shared.DeviceIdentity, "time_zone", None),
    "total_active_energy_built_in_energy": RegisterLocation(
        emma.EmmaBuiltInMeter, "total_active_energy_built_in_energy", None
    ),
    "total_active_energy_external_energy": RegisterLocation(
        emma.EmmaExternalMeter, "total_active_energy_external_energy", None
    ),
    "total_bus_voltage": RegisterLocation(sun2000.Inverter, "total_bus_voltage", None),
    "total_charged_energy": RegisterLocation(emma.Emma, "total_charged_energy", None),
    "total_dc_input_power": RegisterLocation(sun2000.Inverter, "total_dc_input_power", None),
    "total_discharged_energy": RegisterLocation(emma.Emma, "total_discharged_energy", None),
    "total_energy_consumption": RegisterLocation(emma.Emma, "total_energy_consumption", None),
    "total_feed_in_to_grid": RegisterLocation(emma.Emma, "total_feed_in_to_grid", None),
    "total_negative_active_energy_built_in_energy": RegisterLocation(
        emma.EmmaBuiltInMeter, "total_negative_active_energy_built_in_energy", None
    ),
    "total_negative_active_energy_external_energy": RegisterLocation(
        emma.EmmaExternalMeter, "total_negative_active_energy_external_energy", None
    ),
    "total_positive_active_energy_built_in_energy": RegisterLocation(
        emma.EmmaBuiltInMeter, "total_positive_active_energy_built_in_energy", None
    ),
    "total_positive_active_energy_external_energy": RegisterLocation(
        emma.EmmaExternalMeter, "total_positive_active_energy_external_energy", None
    ),
    "total_pv_energy_yield": RegisterLocation(emma.Emma, "total_pv_energy_yield", None),
    "total_supply_from_grid": RegisterLocation(emma.Emma, "total_supply_from_grid", None),
    "unique_id_of_the_software": RegisterLocation(sun2000.ProductInfo, "unique_id_of_the_software", None),
    "wlan_wakeup": RegisterLocation(sun2000.Configuration, "wlan_wakeup", None),
    "yearly_feed_in_to_grid": RegisterLocation(emma.Emma, "yearly_feed_in_to_grid", None),
    "yearly_supply_from_grid": RegisterLocation(emma.Emma, "yearly_supply_from_grid", None),
    "yearly_yield_energy": RegisterLocation(sun2000.Inverter, "yearly_yield_energy", None),
    "yield_this_month": RegisterLocation(emma.Emma, "yield_this_month", None),
    "yield_this_year": RegisterLocation(emma.Emma, "yield_this_year", None),
}
