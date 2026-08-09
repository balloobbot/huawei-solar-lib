"""The register map of an SDongle communication stick."""

from __future__ import annotations

from huawei_solar import register_values as rv
from huawei_solar.components.base import HuaweiComponent
from huawei_solar.fields import (
    i16,
    i32,
    text,
    u16,
    u32,
)


class SDongle(HuaweiComponent):
    """SDongle status, connectivity and 4G traffic counters."""

    wireless_route_access_signal_strength = i16(35104, convert=rv.SDongleWirelessRouteAccessSignalStrength4G)
    monthly_used_traffic_4g = u32(35116, unit="MB")
    monthly_remaining_traffic_4g = u32(35118, unit="MB")
    average_daily_used_traffic_4g = u32(35120, unit="MB")
    traffic_status_4g = u16(35122, convert=rv.SDongleTrafficStatus4G)
    imei_4g = text(35254, 10)
    signal_strength_4g = u16(35264)
    system_4g = text(35266, 10)
    type = u16(37410, convert=rv.SDongleType)
    device_search_status = u16(37411, convert=rv.SDongleDeviceSearchStatus)
    change_sequence_number = u16(37412)
    maximum_devices_allowed = u16(37429)
    carrier_4g = text(37440, 15)
    total_input_power = u32(37498, unit="kW", gain=1000)
    load_power = u32(37500, unit="kW", gain=1000)
    grid_power = i32(37502, unit="kW", gain=1000)
    total_battery_power = i32(37504, unit="kW", gain=1000)
    total_active_power = i32(37516, unit="kW", gain=1000)
    application_layer_heartbeat_period = u16(43064, unit="min", writable=True)
    tcp_heartbeat_period = u16(43065, unit="s", writable=True)
    nms_server = text(43067, 30, writable=True)
    nms_server_port1 = u16(43097, writable=True)
    ssl_encryption = u16(43098, convert=bool, writable=True)
    nms_server_port2 = u16(43099, writable=True)
    port_mode = u16(43100, convert=rv.SDonglePortMode, writable=True)
    registration_status = u16(43101, convert=bool, writable=True)
    unsolicited_report_interval = u16(43134, unit="min", writable=True)
    reported_data_record_period = u16(43311, convert=bool, writable=True)
    ntp_time_synchronization = u16(43343, unit="min", writable=True)
    card_number_4g = text(43386, 10, writable=True)
    network_mode_4g = u16(43430, convert=rv.SDongleNetworkMode4G, writable=True)
    traffic_package_4g = u32(43564, unit="MB", gain=2, writable=True)
    monthly_used_traffic_correction_4g = u32(43566, unit="MB", gain=2)
    device_operation = text(47402, 10)
    device_operation_command = text(47412, 1)
    start_device_search = u16(47413)


class Commands(HuaweiComponent):
    """Write-only command registers.

    The device refuses to read these back, so this component is never
    updated — it exists purely as a target for ``write()``.
    """

    sdongle_reset = u16(40205, writable=True)
    sdongle_connection_port = u16(45038, convert=rv.SDongleConnectionPort, writable=True)
