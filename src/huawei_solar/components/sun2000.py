"""The register map of a SUN2000 inverter and the batteries behind it."""

from __future__ import annotations

from functools import partial

from huawei_solar import register_values as rv
from huawei_solar.components.base import HuaweiComponent
from huawei_solar.fields import (
    ChargeDischargePeriodsField,
    HuaweiLuna2000TimeOfUseField,
    LgResuTimeOfUseField,
    PeakSettingPeriodsField,
    i16,
    i32,
    i32_absolute,
    text,
    timestamp,
    u16,
    u32,
)


class ProductInfo(HuaweiComponent):
    """Static product, hardware and firmware information."""

    pn = text(30025, 10)
    firmware_version = text(30035, 15)
    protocol_version_modbus = u32(30068)
    model_id = u16(30070)
    nb_pv_strings = u16(30071)
    nb_mpp_tracks = u16(30072)
    rated_power = u32(30073, unit="W")
    P_max = u32(30075, unit="W")
    S_max = u32(30077, unit="VA")
    Q_max_out = i32(30079, unit="var")
    Q_max_in = i32(30081, unit="var")
    P_max_real = u32(30083, unit="W")
    S_max_real = u32(30085, unit="VA")
    product_sales_area = text(30105, 2)
    product_software_number = u16(30107)
    product_software_version_number = u16(30108)
    grid_standard_code_protocol_version = u16(30109)
    unique_id_of_the_software = u16(30110)
    number_of_packages_to_be_upgraded = u16(30111)
    hardware_functional_unit_conf_id = u16(30206)
    subdevice_support_flag = u32(30207)
    subdevice_in_position_flag = u32(30209)
    feature_mask_1 = u32(30211)
    feature_mask_2 = u32(30213)
    feature_mask_3 = u32(30215)
    feature_mask_4 = u32(30217)
    realtime_max_active_capability = i32(30366)
    realtime_max_inductive_reactive_capacity = i32(30368)
    offering_name_of_southbound_device_1 = text(30561, 15)
    offering_name_of_southbound_device_2 = text(30576, 15)
    offering_name_of_southbound_device_3 = text(30591, 15)
    hardware_version = text(31000, 15)
    monitoring_board_sn = text(31015, 10)
    monitoring_software_version = text(31025, 15)
    master_dsp_version = text(31040, 15)
    slave_dsp_version = text(31055, 15)
    cpld_version = text(31070, 15)
    afci_version = text(31085, 15)
    builtin_pid_version = text(31100, 15)
    dc_mbus_version = text(31115, 15)
    el_module_version = text(31130, 15)
    afci_2_version = text(31145, 15)
    regkey = text(31200, 10)


class Inverter(HuaweiComponent):
    """Live inverter telemetry: state, alarms, grid and yield."""

    state_1 = u16(32000, convert=partial(rv.bitfield_decoder, rv.STATE_CODES_1))
    state_2 = u16(32002, convert=partial(rv.bitfield_decoder, rv.STATE_CODES_2))
    state_3 = u32(32003, convert=partial(rv.bitfield_decoder, rv.STATE_CODES_3))
    alarm_1 = u16(32008, convert=partial(rv.bitfield_decoder, rv.ALARM_CODES_1), nan=None)
    alarm_2 = u16(32009, convert=partial(rv.bitfield_decoder, rv.ALARM_CODES_2), nan=None)
    alarm_3 = u16(32010, convert=partial(rv.bitfield_decoder, rv.ALARM_CODES_3))
    input_power = i32(32064, unit="W")
    grid_voltage = u16(32066, unit="V", gain=10)
    line_voltage_A_B = u16(32066, unit="V", gain=10)
    line_voltage_B_C = u16(32067, unit="V", gain=10)
    line_voltage_C_A = u16(32068, unit="V", gain=10)
    phase_A_voltage = u16(32069, unit="V", gain=10)
    phase_B_voltage = u16(32070, unit="V", gain=10)
    phase_C_voltage = u16(32071, unit="V", gain=10)
    grid_current = i32(32072, unit="A", gain=1000)
    phase_A_current = i32(32072, unit="A", gain=1000)
    phase_B_current = i32(32074, unit="A", gain=1000)
    phase_C_current = i32(32076, unit="A", gain=1000)
    day_active_power_peak = i32(32078, unit="W")
    active_power = i32(32080, unit="W")
    reactive_power = i32(32082, unit="var")
    power_factor = i16(32084, gain=1000)
    grid_frequency = u16(32085, unit="Hz", gain=100)
    efficiency = u16(32086, unit="%", gain=100)
    internal_temperature = i16(32087, unit="°C", gain=10)
    insulation_resistance = u16(32088, unit="MOhm", gain=1000)
    device_status = u16(32089, convert=rv.DEVICE_STATUS_DEFINITIONS)
    fault_code = u16(32090)
    startup_time = timestamp(32091)
    shutdown_time = timestamp(32093)
    active_power_fast = i32(32095, unit="W")
    accumulated_yield_energy = u32(32106, unit="kWh", gain=100)
    total_dc_input_power = u32(32108, unit="kWh", gain=100)
    current_electricity_generation_statistics_time = timestamp(32110)
    hourly_yield_energy = u32(32112, unit="kWh", gain=100)
    daily_yield_energy = u32(32114, unit="kWh", gain=100)
    monthly_yield_energy = u32(32116, unit="kWh", gain=100)
    yearly_yield_energy = u32(32118, unit="kWh", gain=100)
    latest_active_alarm_sn = u32(32172)
    latest_historical_alarm_sn = u32(32174)
    total_bus_voltage = i16(32176, unit="V", gain=10)
    max_pv_voltage = i16(32177, unit="V", gain=10)
    min_pv_voltage = i16(32178, unit="V", gain=10)
    average_pv_negative_voltage_to_ground = i16(32179, unit="V", gain=10)
    min_pv_negative_voltage_to_ground = i16(32180, unit="V", gain=10)
    max_pv_negative_voltage_to_ground = i16(32181, unit="V", gain=10)
    inverter_to_pe_voltage_tolerance = u16(32182, unit="V")
    iso_feature_information = u16(32183)
    builtin_pid_running_status = u16(32190)
    pv_negative_voltage_to_ground = i16(32191, unit="V", gain=10)
    cumulative_dc_energy_yield_mppt1 = u32(32212, unit="kWh", gain=100)
    cumulative_dc_energy_yield_mppt2 = u32(32214, unit="kWh", gain=100)
    cumulative_dc_energy_yield_mppt3 = u32(32216, unit="kWh", gain=100)
    cumulative_dc_energy_yield_mppt4 = u32(32218, unit="kWh", gain=100)
    cumulative_dc_energy_yield_mppt5 = u32(32220, unit="kWh", gain=100)
    cumulative_dc_energy_yield_mppt6 = u32(32222, unit="kWh", gain=100)
    cumulative_dc_energy_yield_mppt7 = u32(32224, unit="kWh", gain=100)
    cumulative_dc_energy_yield_mppt8 = u32(32226, unit="kWh", gain=100)
    cumulative_dc_energy_yield_mppt9 = u32(32228, unit="kWh", gain=100)
    cumulative_dc_energy_yield_mppt10 = u32(32230, unit="kWh", gain=100)


class PVString(HuaweiComponent):
    """One PV string's voltage and current.

    Indexed 1..24; the strings are a regular two-register repeat.
    """

    voltage = i16(32016, unit="V", gain=10, stride=2)
    current = i16(32017, unit="A", gain=100, stride=2)


class Diagnostics(HuaweiComponent):
    """Temperatures, running times and adjustment diagnostics."""

    capbank_running_time = u32(35000, unit="hour", gain=10)
    internal_fan_1_running_time = u32(35002, unit="hour", gain=10)
    inv_module_a_temp = i16(35021, unit="°C", gain=10)
    inv_module_b_temp = i16(35022, unit="°C", gain=10)
    inv_module_c_temp = i16(35023, unit="°C", gain=10)
    anti_reverse_module_1_temp = i16(35024, unit="°C", gain=10)
    output_board_relay_ambient_temp_max = i16(35025, unit="°C", gain=10)
    anti_reverse_module_2_temp = i16(35027, unit="°C", gain=10)
    dc_terminal_1_2_max_temp = i16(35028, unit="°C", gain=10)
    ac_terminal_1_2_3_max_temp = i16(35029, unit="°C", gain=10)
    phase_a_dc_component_dci = i16(35038, unit="A", gain=1000)
    phase_b_dc_component_dci = i16(35039, unit="A", gain=1000)
    phase_c_dc_component_dci = i16(35040, unit="A", gain=1000)
    leakage_current_rcd = i16(35041, unit="mA")
    positive_bus_voltage = i16(35042, unit="V", gain=10)
    negative_bus_voltage = i16(35043, unit="V", gain=10)
    bus_negative_voltage_to_ground = i16(35044, unit="V", gain=10)
    active_power_adjustment_mode = u16(35300)
    active_power_adjustment_value = u32(35301)
    active_power_adjustment_command = u16(35303)


class StorageUnit(HuaweiComponent):
    """One of the two storage units.

    Indexed 1..2. Huawei's second unit is *not* a regular repeat of the
    first: every field sits at its own arbitrary offset, so each carries
    its own ``stride`` rather than the component sharing one.
    """

    running_status = u16(37000, convert=rv.StorageStatus, stride=741)
    charge_discharge_power = i32(37001, unit="W", stride=742)
    bus_voltage = u16(37003, unit="V", gain=10, stride=747)
    state_of_capacity = u16(37004, unit="%", gain=10, stride=734)
    current_day_charge_capacity = u32(37015, unit="kWh", gain=100, stride=731)
    current_day_discharge_capacity = u32(37017, unit="kWh", gain=100, stride=731)
    bus_current = i16(37021, unit="A", gain=10, stride=730)
    battery_temperature = i16(37022, unit="°C", gain=10, stride=730)
    serial_number = text(37052, 10, stride=648)
    total_charge = u32(37066, unit="kWh", gain=100, stride=687)
    total_discharge = u32(37068, unit="kWh", gain=100, stride=687)
    software_version = text(37814, 15, stride=-15)
    product_model = u16(47000, convert=rv.StorageProductModel, stride=89)
    no = u16(47107, stride=1)
    pack_1_no = u16(47750, stride=3)
    pack_2_no = u16(47751, stride=3)
    pack_3_no = u16(47752, stride=3)


class StorageUnit1Only(HuaweiComponent):
    """Storage registers the first unit reports and the second does not."""

    working_mode_b = u16(37006, convert=rv.StorageWorkingModesB)
    rated_charge_power = u32(37007, unit="W")
    rated_discharge_power = u32(37009, unit="W")
    fault_id = u16(37014)
    remaining_charge_dis_charge_time = u16(37025, unit="min")
    dcdc_version = text(37026, 10)
    bms_version = text(37036, 10)


class StorageSettings(HuaweiComponent):
    """Battery configuration: working mode, schedules and limits."""

    storage_maximum_charge_power = u32(37046, unit="W")
    storage_maximum_discharge_power = u32(37048, unit="W")
    storage_rated_capacity = u32(37758, unit="Wh")
    storage_state_of_capacity = u16(37760, unit="%", gain=10)
    storage_running_status = u16(37762, convert=rv.StorageStatus)
    storage_bus_voltage = u16(37763, unit="V", gain=10)
    storage_bus_current = i16(37764, unit="A", gain=10)
    storage_charge_discharge_power = i32(37765, unit="W")
    storage_total_charge = u32(37780, unit="kWh", gain=100)
    storage_total_discharge = u32(37782, unit="kWh", gain=100)
    storage_current_day_charge_capacity = u32(37784, unit="kWh", gain=100)
    storage_current_day_discharge_capacity = u32(37786, unit="kWh", gain=100)
    storage_unit_soh_calibration_status = u16(37926)
    storage_unit_soh_calibration_release_lower_limit_of_soc = u16(37927)
    storage_working_mode_a = i16(47004, convert=rv.StorageWorkingModesA)
    storage_time_of_use_price = i16(47027, convert=bool)
    storage_lg_resu_time_of_use_price_periods = LgResuTimeOfUseField(47028, count=41, writable=True)
    storage_lcoe = u32(47069, gain=1000)
    storage_maximum_charging_power = u32(47075, unit="W", writable=True)
    storage_maximum_discharging_power = u32(47077, unit="W", writable=True)
    storage_power_limit_grid_tied_point = i32(47079, unit="W")
    storage_charging_cutoff_capacity = u16(47081, unit="%", gain=10, writable=True)
    storage_discharging_cutoff_capacity = u16(47082, unit="%", gain=10, writable=True)
    storage_forced_charging_and_discharging_period = u16(47083, unit="min", writable=True)
    storage_forced_charging_and_discharging_power = i32(47084, unit="W")
    storage_working_mode_settings = u16(47086, convert=rv.StorageWorkingModesC, writable=True)
    storage_charge_from_grid_function = u16(47087, convert=bool, writable=True)
    storage_grid_charge_cutoff_state_of_charge = u16(47088, unit="%", gain=10, writable=True)
    storage_forcible_charge_discharge_soc = u16(47101, unit="%", gain=10, writable=True)
    storage_backup_power_state_of_charge = u16(47102, unit="%", gain=10, writable=True)
    storage_fixed_charging_and_discharging_periods = ChargeDischargePeriodsField(47200, count=41, writable=True)
    storage_power_of_charge_from_grid = u32(47242, unit="W", writable=True)
    storage_maximum_power_of_charge_from_grid = u32(47244, unit="W", writable=True)
    storage_forcible_charge_discharge_setting_mode = u16(
        47246, convert=rv.StorageForcibleChargeDischargeTargetMode, writable=True
    )
    storage_forcible_charge_power = u32(47247, writable=True)
    storage_forcible_discharge_power = u32(47249, writable=True)
    storage_huawei_luna2000_time_of_use_charging_and_discharging_periods = HuaweiLuna2000TimeOfUseField(
        47255, count=43, writable=True
    )
    storage_excess_pv_energy_use_in_tou = u16(47299, convert=rv.StorageExcessPvEnergyUseInTOU, writable=True)
    storage_capacity_control_mode = u16(47954, convert=rv.StorageCapacityControlMode, writable=True)
    storage_capacity_control_soc_peak_shaving = u16(47955, unit="%", gain=10, writable=True)
    storage_capacity_control_periods = PeakSettingPeriodsField(47956, count=64, writable=True)


class PowerMeter(HuaweiComponent):
    """The power meter the inverter reads on the grid connection."""

    meter_status = u16(37100, convert=rv.MeterStatus)
    grid_A_voltage = i32(37101, unit="V", gain=10)
    grid_B_voltage = i32(37103, unit="V", gain=10)
    grid_C_voltage = i32(37105, unit="V", gain=10)
    active_grid_A_current = i32(37107, unit="A", gain=100)
    active_grid_B_current = i32(37109, unit="A", gain=100)
    active_grid_C_current = i32(37111, unit="A", gain=100)
    power_meter_active_power = i32(37113, unit="W")
    power_meter_reactive_power = i32(37115, unit="var")
    active_grid_power_factor = i16(37117, gain=1000)
    active_grid_frequency = i16(37118, unit="Hz", gain=100)
    grid_exported_energy = i32_absolute(37119, unit="kWh", gain=100)
    grid_accumulated_energy = i32(37121, unit="kWh", gain=100)
    grid_accumulated_reactive_power = i32(37123, unit="kvarh", gain=100)
    meter_type = u16(37125, convert=rv.MeterType)
    active_grid_A_B_voltage = i32(37126, unit="V", gain=10)
    active_grid_B_C_voltage = i32(37128, unit="V", gain=10)
    active_grid_C_A_voltage = i32(37130, unit="V", gain=10)
    active_grid_A_power = i32(37132, unit="W")
    active_grid_B_power = i32(37134, unit="W")
    active_grid_C_power = i32(37136, unit="W")
    meter_type_check = u16(37138, convert=rv.MeterTypeCheck)


class Optimizers(HuaweiComponent):
    """How many optimizers are configured and online."""

    nb_optimizers = u16(37200)
    nb_online_optimizers = u16(37201)


class BatteryPack(HuaweiComponent):
    """One battery pack.

    Indexed 1..6, three packs per storage unit. The main block repeats
    every 42 registers, but the calibration status and the temperature
    pair live in separate, more tightly packed blocks of their own.
    """

    soh_calibration_status = u16(37920, stride=1)
    serial_number = text(38200, 10, stride=42)
    firmware_version = text(38210, 15, stride=42)
    working_status = u16(38228, stride=42)
    state_of_capacity = u16(38229, unit="%", gain=10, stride=42)
    charge_discharge_power = i32(38233, unit="W", stride=42)
    voltage = u16(38235, unit="V", gain=10, stride=42)
    current = i16(38236, unit="A", gain=10, stride=42)
    total_charge = u32(38238, unit="kWh", gain=100, stride=42)
    total_discharge = u32(38240, unit="kWh", gain=100, stride=42)
    maximum_temperature = i16(38452, unit="°C", gain=10, stride=2)
    minimum_temperature = i16(38453, unit="°C", gain=10, stride=2)


class Configuration(HuaweiComponent):
    """Inverter settings: grid code, power control and time."""

    system_time = timestamp(40000)
    system_time_raw = u32(40000, unit="seconds")
    q_u_characteristic_curve_model = u16(40037, writable=True)
    q_u_scheduling_trigger_power_percentage = i16(40038, writable=True)
    power_factor_2 = i16(40122, gain=1000, writable=True)
    reactive_power_compensation = i16(40123, gain=1000, writable=True)
    reactive_power_adjustment_time = u16(40124, unit="seconds", writable=True)
    active_power_percentage_derating = i16(40125, unit="%", gain=10, writable=True)
    active_power_fixed_value_derating = u32(40126, unit="W", writable=True)
    reactive_power_compensation_at_night = i16(40128, gain=1000, writable=True)
    fixed_reactive_power_at_night = i32(40129, unit="var", writable=True)
    characteristic_curve_reactive_power_adjustment_time = u16(40196, unit="seconds", writable=True)
    percent_apparent_power = u16(40197, unit="%", gain=10, writable=True)
    q_u_scheduling_exit_power_percentage = i16(40198, unit="%", writable=True)
    grid_code = u16(42000, convert=rv.GRID_CODES)
    mppt_multimodal_scanning = u16(42054, convert=bool, writable=True)
    mppt_scanning_interval = u16(42055, unit="minutes", writable=True)
    mppt_predicted_power = u32(42056, unit="W")
    maximum_active_power = u32(42178, unit="W")
    wlan_wakeup = i16(45052, convert=rv.WlanWakeup, writable=True)
    forcible_charge_discharge_write = u16(47100, convert=rv.StorageForcibleChargeDischarge, writable=True)
    active_power_control_mode = u16(47415, convert=rv.ActivePowerControlMode, writable=True)
    maximum_feed_grid_power_watt = i32(47416, unit="W", writable=True)
    maximum_feed_grid_power_percent = i16(47418, unit="%", gain=10, writable=True)
    remote_charge_discharge_control_mode = i16(47589, convert=rv.RemoteChargeDischargeControlMode, writable=True)
    dongle_plant_maximum_charge_from_grid_power = u32(47590, unit="W", writable=True)
    backup_switch_to_off_grid = u16(47604, writable=True)
    backup_voltage_independent_operation = u16(47605, convert=rv.BackupVoltageIndependentOperation, writable=True)
    default_maximum_feed_in_power = i32(47675, unit="W", writable=True)
    default_active_power_change_gradient = u32(47677, unit="%/s", gain=1000)


class Commands(HuaweiComponent):
    """Write-only command registers.

    The device refuses to read these back, so this component is never
    updated — it exists purely as a target for ``write()``.
    """

    startup = u16(40200, writable=True)
    shutdown = u16(40201, writable=True)
