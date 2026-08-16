"""The Modbus link to Huawei Solar devices.

Huawei devices are reached over a single shared Modbus link: the inverter the
cable is plugged into answers on its own unit id, and every sub-device (extra
inverters, batteries, the power meter, an SDongle) answers on another unit id
behind it. ``modbus_connection`` models that directly — one
:class:`HuaweiModbusConnection`, one :meth:`for_unit` handle per device.

Two things this library needs are not on the ``ModbusUnit`` protocol, so they
live in a tmodbus-specific subclass here:

* Huawei's private function code ``0x41``, used for the login handshake and for
  the file-upload flow that carries optimizer data. It needs a raw-PDU seam,
  which ``ModbusUnit`` deliberately does not offer.
* ``read_device_identification`` with a non-default device code and object id.
  ``ModbusUnit.read_device_identification()`` takes no arguments and the tmodbus
  backend hardcodes ``(1, 0)``; Huawei's device inventory lives at ``(3, 0x87)``.

Both are reached through :class:`SupportsHuaweiPdu`, so the rest of the library
stays backend-neutral and degrades with a clear error on a backend that cannot
provide them.
"""

from __future__ import annotations

import logging
from functools import partial
from typing import TYPE_CHECKING, Any, Literal, Protocol, runtime_checkable

from modbus_connection import (
    ModbusSerialParams,
    ModbusTcpParams,
)
from modbus_connection.tmodbus import ModbusConnection as _TmodbusConnection
from modbus_connection.tmodbus import TmodbusUnit as _TmodbusUnit
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine

    from tmodbus.pdu.base import RT, BaseClientPDU

#: The ReadDevId codes tmodbus accepts for function code 0x2B / 0x0E.
DeviceCode = Literal[1, 2, 3, 4]

_LOGGER = logging.getLogger(__name__)

DEFAULT_TCP_PORT = 502
DEFAULT_BAUDRATE = 9600

DEFAULT_UNIT_ID = 0
DEFAULT_TIMEOUT = 10  # especially the SDongle can react quite slowly
DEFAULT_SCAN_TIMEOUT = 3  # short timeout for scanning — responding devices reply in milliseconds

# Huawei inverters drop requests that arrive back-to-back, so every frame on the
# link is spaced. This is a property of the link, not of one consumer, which is
# why it belongs on the connection rather than in a caller's own pacing.
DEFAULT_MESSAGE_SPACING = 0.05
# The inverter needs a moment after the socket opens before it answers reliably.
DEFAULT_CONNECT_DELAY = 1.0

#: Huawei's private Modbus exception code, returned when the request needs a
#: login session that is not (or no longer) established.
PERMISSION_DENIED_CODE = 0x80


def _response_retry() -> AsyncRetrying:
    """Retry a request that timed out.

    ``modbus_connection`` turns per-request retries off in both backends and
    exposes no knob to configure them, so the policy this library has always had
    — three attempts, exponential backoff — is applied here instead.
    """
    return AsyncRetrying(
        wait=wait_exponential(multiplier=1, min=1, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(TimeoutError),
        reraise=True,
    )


def _no_retry() -> AsyncRetrying:
    """Do not retry: used while scanning, where a silent unit id means 'absent'."""
    return AsyncRetrying(stop=stop_after_attempt(1), reraise=True)


@runtime_checkable
class SupportsHuaweiPdu(Protocol):
    """A unit that can carry Huawei's private function-code 0x41 traffic."""

    async def execute_pdu(self, pdu: BaseClientPDU[RT]) -> RT:
        """Send a raw application PDU to this unit and return its decoded response."""
        ...

    async def read_device_identification_objects(self, device_code: DeviceCode, object_id: int) -> dict[int, bytes]:
        """Read FC 0x2B/0x0E objects for an arbitrary device code and object id."""
        ...


class HuaweiUnit(_TmodbusUnit):
    """A unit on a Huawei link.

    Adds the raw-PDU seam and the timeout retry policy on top of the stock
    tmodbus unit. Only the operations this library actually issues are retried;
    the rest of the ``ModbusUnit`` surface is inherited unchanged.
    """

    def __init__(self, connection: HuaweiModbusConnection, unit_id: int) -> None:
        """Create a unit handle bound to ``unit_id``."""
        super().__init__(connection, unit_id)
        self._retry = connection.retry_factory

    async def _retrying[T](self, operation: Callable[[], Coroutine[Any, Any, T]]) -> T:
        """Run ``operation`` under this connection's retry policy.

        tenacity only awaits what it recognises as a coroutine function, so
        ``operation`` has to be one — a lambda wrapping the call is handed back
        un-awaited as the result, and never retried.
        """
        return await self._retry()(operation)

    async def read_holding_registers(self, address: int, count: int) -> list[int]:
        """Read holding registers, retrying on timeout."""
        return await self._retrying(partial(super().read_holding_registers, address, count))

    async def write_register(self, address: int, value: int) -> None:
        """Write a single holding register, retrying on timeout."""
        await self._retrying(partial(super().write_register, address, value))

    async def write_registers(self, address: int, values: list[int]) -> None:
        """Write multiple holding registers, retrying on timeout."""
        await self._retrying(partial(super().write_registers, address, values))

    async def execute_pdu(self, pdu: BaseClientPDU[RT]) -> RT:
        """Send a raw application PDU to this unit.

        Reaches past the ``ModbusUnit`` protocol into the tmodbus client that
        backs it, because the protocol has no raw-PDU seam. Connecting and
        pacing are done the same way the typed operations do them, so a PDU sent
        here queues behind ordinary reads instead of racing them.
        """
        await self._conn.connect()
        return await self._retrying(partial(self._execute_paced, pdu))

    async def _execute_paced(self, pdu: BaseClientPDU[RT]) -> RT:
        async with self._conn._pacer.paced(self._unit_id):  # noqa: SLF001
            return await self._client.execute(pdu)

    async def read_device_identification_objects(self, device_code: DeviceCode, object_id: int) -> dict[int, bytes]:
        """Read FC 0x2B/0x0E objects for an arbitrary device code and object id.

        ``ModbusUnit.read_device_identification()`` takes no arguments and the
        backend hardcodes the basic ``(1, 0)`` request, which cannot reach
        Huawei's device inventory at ``(3, 0x87)``.
        """
        await self._conn.connect()

        async def _read() -> dict[int, bytes]:
            async with self._conn._pacer.paced(self._unit_id):  # noqa: SLF001
                return await self._client.read_device_identification(
                    device_code=device_code,
                    object_id=object_id,
                )

        return await self._retrying(_read)


class HuaweiModbusConnection(_TmodbusConnection):
    """A shared Modbus link to a Huawei installation."""

    def __init__(
        self,
        params: ModbusTcpParams | ModbusSerialParams,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        message_spacing: float = DEFAULT_MESSAGE_SPACING,
        connect_delay: float = DEFAULT_CONNECT_DELAY,
        retry_factory: Callable[[], AsyncRetrying] = _response_retry,
    ) -> None:
        """Create a connection to a Huawei installation."""
        super().__init__(
            params,
            timeout=timeout,
            message_spacing=message_spacing,
            connect_delay=connect_delay,
        )
        self.retry_factory = retry_factory

    def for_unit(self, unit_id: int) -> HuaweiUnit:
        """Return a handle for the device answering on ``unit_id``."""
        return HuaweiUnit(self, unit_id)


def create_tcp_connection(
    host: str,
    port: int = DEFAULT_TCP_PORT,
    *,
    timeout: float = DEFAULT_TIMEOUT,
) -> HuaweiModbusConnection:
    """Create a connection to a Huawei installation reachable over TCP."""
    return HuaweiModbusConnection(ModbusTcpParams(host=host, port=port), timeout=timeout)


def create_rtu_connection(
    port: str,
    *,
    baudrate: int = DEFAULT_BAUDRATE,
    timeout: float = DEFAULT_TIMEOUT,
) -> HuaweiModbusConnection:
    """Create a connection to a Huawei installation reachable over a serial line."""
    return HuaweiModbusConnection(ModbusSerialParams(device=port, baudrate=baudrate), timeout=timeout)


def create_scan_tcp_connection(
    host: str,
    port: int = DEFAULT_TCP_PORT,
    *,
    timeout: float = DEFAULT_SCAN_TIMEOUT,
) -> HuaweiModbusConnection:
    """Create a TCP connection tuned for probing unit ids.

    A unit id that does not answer is absent, not slow, so retrying it only
    makes a scan of the whole address space take minutes instead of seconds.
    """
    return HuaweiModbusConnection(
        ModbusTcpParams(host=host, port=port),
        timeout=timeout,
        retry_factory=_no_retry,
    )


def create_scan_rtu_connection(
    port: str,
    *,
    baudrate: int = DEFAULT_BAUDRATE,
    timeout: float = DEFAULT_SCAN_TIMEOUT,
) -> HuaweiModbusConnection:
    """Create a serial connection tuned for probing unit ids."""
    return HuaweiModbusConnection(
        ModbusSerialParams(device=port, baudrate=baudrate),
        timeout=timeout,
        retry_factory=_no_retry,
    )


def require_pdu_support(unit: Any) -> SupportsHuaweiPdu:  # noqa: ANN401
    """Return ``unit`` as a PDU-capable unit, or explain why it is not.

    Reading files and logging in both ride Huawei's private function code
    ``0x41``. Any backend can serve the register traffic; only one built here
    can carry a raw PDU.
    """
    if isinstance(unit, SupportsHuaweiPdu):
        return unit
    msg = (
        f"{type(unit).__name__} cannot send Huawei's private function code 0x41. "
        "Login and file reads need a unit from a HuaweiModbusConnection."
    )
    raise TypeError(msg)
