"""Talk to a Huawei device below the register map.

Everything here rides Huawei's private function code ``0x41`` or needs a Modbus
function ``modbus_connection``'s typed unit does not fully expose, so each takes
a :class:`~huawei_solar.connection.SupportsHuaweiPdu` rather than a plain
``ModbusUnit``. It also carries the translation from ``modbus_connection``'s
exceptions to this library's own.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import TYPE_CHECKING, Literal

from modbus_connection import (
    ModbusConnectionError,
    ModbusError,
    ModbusExceptionError,
    ModbusTimeoutError,
)
from tmodbus.utils.crc import calculate_crc16

from huawei_solar.connection import PERMISSION_DENIED_CODE, DeviceCode, require_pdu_support
from huawei_solar.exceptions import (
    ConnectionInterruptedException,
    PermissionDeniedError,
    ReadException,
    WriteException,
)
from huawei_solar.modbus_pdu import (
    CompleteUploadPDU,
    LoginPDU,
    LoginRequestChallengePDU,
    StartFileUploadPDU,
    UploadFileFramePDU,
)

if TYPE_CHECKING:
    from collections.abc import Iterator

    from modbus_connection import ModbusUnit

_LOGGER = logging.getLogger(__name__)

#: The register the inverter watches to decide a login session is still alive.
HEARTBEAT_REGISTER = 49999


@contextmanager
def translating(action: str, *, failure: Literal["read", "write"] = "read") -> Iterator[None]:
    """Turn ``modbus_connection`` errors into this library's exceptions.

    A timeout is deliberately let through: it is already a ``TimeoutError``, and
    callers — Home Assistant's update coordinator among them — tell "the device
    did not answer" apart from "the device refused" by catching that.
    """
    error = ReadException if failure == "read" else WriteException
    try:
        yield
    except ModbusTimeoutError:
        raise
    except ModbusExceptionError as err:
        if err.exception_code == PERMISSION_DENIED_CODE:
            msg = f"Not allowed to {action} without being logged in"
            raise PermissionDeniedError(msg) from err
        msg = f"Failed to {action}: device returned Modbus exception {err.exception_code}"
        raise error(msg, modbus_exception_code=err.exception_code) from err
    except ModbusConnectionError as err:
        msg = f"Connection failed while trying to {action}"
        raise ConnectionInterruptedException(msg) from err
    except ModbusError as err:
        msg = f"Failed to {action}: {err}"
        raise error(msg) from err


async def login(unit: ModbusUnit, username: str, password: str) -> bool:
    """Open a login session on the device.

    Two round trips over function code ``0x41``: the device offers a challenge,
    and the answer proves knowledge of the password without sending it. The
    device's own answer is checked in turn, so a man in the middle cannot pass
    itself off as the inverter.
    """
    pdu_unit = require_pdu_support(unit)
    _LOGGER.debug("Logging in '%s'", username)
    with translating(f"log in as '{username}'"):
        challenge = await pdu_unit.execute_pdu(LoginRequestChallengePDU())
        return await pdu_unit.execute_pdu(LoginPDU(username, password, challenge))


async def heartbeat(unit: ModbusUnit) -> bool:
    """Tell the device the login session is still in use.

    The session lapses without this, and every write starts failing with a
    permission error. Returns whether the device accepted it; a device that
    refuses or has gone away is reported rather than raised, because the caller
    is a background loop that should stop quietly.
    """
    if not unit.connected:
        return False
    try:
        await unit.write_register(HEARTBEAT_REGISTER, 0x1)
    except ModbusExceptionError as err:
        _LOGGER.warning(
            "Received an error response when writing to the heartbeat register: %s",
            err.exception_code,
        )
        return False
    except (ModbusError, TimeoutError):
        _LOGGER.exception("Exception during heartbeat")
        return False
    else:
        _LOGGER.debug("Heartbeat succeeded")
        return True


async def read_file(unit: ModbusUnit, file_type: int, customized_data: bytes | None = None) -> bytes:
    """Read a 'file' from the device.

    Huawei ships bulk data — the optimizer history above all — as a file rather
    than as registers: a start request that answers with the length and the
    frame size, one request per frame, and a final request returning a CRC over
    the whole thing. Defined in 6.3.7.1 of the Solar Inverter Modbus Interface
    Definitions.
    """
    pdu_unit = require_pdu_support(unit)
    _LOGGER.debug("Reading file %#x", file_type)

    with translating(f"read file {file_type:#x}"):
        start = await pdu_unit.execute_pdu(
            StartFileUploadPDU(file_type=file_type, customised_data=customized_data or b""),
        )

        file_data = b""
        frame_no = 0
        while (frame_no * start.data_frame_length) < start.file_length:
            frame = await pdu_unit.execute_pdu(UploadFileFramePDU(file_type=file_type, frame_no=frame_no))
            file_data += frame.frame_data
            frame_no += 1

        file_crc = await pdu_unit.execute_pdu(CompleteUploadPDU(file_type=file_type))

    # The device reports the CRC with its bytes the other way round from how it
    # is computed over the data.
    swapped_crc = ((file_crc << 8) & 0xFF00) | ((file_crc >> 8) & 0x00FF)
    if (calculated_crc := int.from_bytes(calculate_crc16(file_data))) != swapped_crc:
        msg = f"Computed CRC {calculated_crc:04x} for file {file_type} does not match expected value {swapped_crc:04x}"
        raise ReadException(msg)

    return file_data


async def read_device_identification(unit: ModbusUnit, device_code: DeviceCode, object_id: int) -> dict[int, bytes]:
    """Read the device-identification objects starting at ``object_id``."""
    pdu_unit = require_pdu_support(unit)
    with translating("read device identification"):
        return await pdu_unit.read_device_identification_objects(device_code, object_id)
