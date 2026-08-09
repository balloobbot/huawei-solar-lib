"""Tests for the traffic that rides Huawei's private function code 0x41.

Login and file reads cannot go through ``modbus_connection``'s typed unit at
all, so they run over the raw-PDU seam in :mod:`huawei_solar.connection`. These
tests answer the PDUs the way an inverter does — including computing the login
digests — so the wire format is exercised rather than stubbed.
"""

from __future__ import annotations

import hmac
import struct
from hashlib import sha256
from typing import Any

import pytest
from huawei_solar.exceptions import PermissionDeniedError, ReadException
from huawei_solar.modbus_pdu import (
    CompleteUploadPDU,
    LoginPDU,
    LoginRequestChallengePDU,
    StartFileUploadPDU,
    UploadFileFramePDU,
)
from modbus_connection import IllegalDataAddressError, ModbusExceptionError
from modbus_connection.mock import MockModbusConnection, MockModbusUnit
from tmodbus.utils.crc import calculate_crc16

from huawei_solar import session

INVERTER_CHALLENGE = bytes(range(16))
PASSWORD = "hunter2"  # noqa: S105 — the fake inverter's password
FILE_TYPE = 0x44
FRAME_SIZE = 8


def _digest(password: str, seed: bytes) -> bytes:
    return hmac.digest(key=sha256(password.encode()).digest(), msg=seed, digest=sha256)


class FakeInverter:
    """Answer Huawei's 0x41 sub-functions the way an inverter does."""

    def __init__(self, password: str = PASSWORD, file_data: bytes = b"") -> None:
        """Set up an inverter that accepts ``password``."""
        self.password = password
        self.file_data = file_data
        self.logged_in = False
        self.reject_login = False
        self.frames_served: list[int] = []

    def respond(self, pdu: Any) -> bytes:
        """Build the response bytes for a request PDU."""
        if isinstance(pdu, LoginRequestChallengePDU):
            return struct.pack(">BBB", 0x41, 0x24, 17) + INVERTER_CHALLENGE + b"\x00"

        if isinstance(pdu, LoginPDU):
            if self.reject_login:
                return struct.pack(">BBB?B", 0x41, 0x25, 2, True, 0)  # noqa: FBT003 — the wire's failure flag
            # Prove we know the password too, over the client's own challenge.
            mac = _digest(self.password, pdu.client_challenge)
            self.logged_in = True
            return struct.pack(">BBB?B", 0x41, 0x25, 2 + len(mac), False, len(mac)) + mac  # noqa: FBT003

        if isinstance(pdu, StartFileUploadPDU):
            if not self.logged_in:
                raise ModbusExceptionError(0x80, "permission denied")
            return struct.pack(">BBBBLB", 0x41, 0x05, 6, FILE_TYPE, len(self.file_data), FRAME_SIZE)

        if isinstance(pdu, UploadFileFramePDU):
            self.frames_served.append(pdu.frame_no)
            chunk = self.file_data[pdu.frame_no * FRAME_SIZE : (pdu.frame_no + 1) * FRAME_SIZE]
            return struct.pack(">BBBBH", 0x41, 0x06, 3 + len(chunk), FILE_TYPE, pdu.frame_no) + chunk

        if isinstance(pdu, CompleteUploadPDU):
            crc = int.from_bytes(calculate_crc16(self.file_data))
            swapped = ((crc << 8) & 0xFF00) | ((crc >> 8) & 0x00FF)
            return struct.pack(">BBBBH", 0x41, 0x0C, 3, FILE_TYPE, swapped)

        msg = f"FakeInverter got an unexpected PDU: {pdu}"
        raise AssertionError(msg)


class PduUnit(MockModbusUnit):
    """A mock unit that also carries raw PDUs, as HuaweiUnit does."""

    def __init__(self, connection: MockModbusConnection, unit_id: int, inverter: FakeInverter) -> None:
        """Bind this unit to the inverter answering its PDUs."""
        super().__init__(connection, unit_id)
        self.inverter = inverter

    async def execute_pdu(self, pdu: Any) -> Any:
        """Send a request PDU and decode what the inverter answers."""
        await self._ensure_connected()
        pdu.encode_request()  # exercise the request encoder too
        return pdu.decode_response(self.inverter.respond(pdu))

    async def read_device_identification_objects(self, device_code: int, object_id: int) -> dict[int, bytes]:
        """Answer an identification request with a recognisable stand-in."""
        return {object_id: bytes([device_code])}


@pytest.fixture
def inverter() -> FakeInverter:
    """Return an inverter with a small file to serve."""
    return FakeInverter(file_data=bytes(range(20)))


@pytest.fixture
def pdu_unit(inverter: FakeInverter) -> PduUnit:
    """Return a PDU-capable unit talking to that inverter."""
    return PduUnit(MockModbusConnection(), 1, inverter)


async def test_login_succeeds_and_verifies_the_inverter(pdu_unit: PduUnit, inverter: FakeInverter) -> None:
    assert await session.login(pdu_unit, "installer", inverter.password) is True
    assert inverter.logged_in


async def test_login_rejected_by_the_inverter(pdu_unit: PduUnit, inverter: FakeInverter) -> None:
    inverter.reject_login = True
    assert await session.login(pdu_unit, "installer", "wrong") is False


async def test_login_detects_an_impostor(pdu_unit: PduUnit, inverter: FakeInverter) -> None:
    """The device has to answer the client's challenge with the right digest."""
    inverter.password = "a-different-password"  # noqa: S105

    with pytest.raises(ValueError, match="invalid challenge answer"):
        await session.login(pdu_unit, "installer", PASSWORD)


async def test_read_file_reassembles_frames_and_checks_the_crc(
    pdu_unit: PduUnit,
    inverter: FakeInverter,
) -> None:
    await session.login(pdu_unit, "installer", inverter.password)

    assert await session.read_file(pdu_unit, FILE_TYPE) == inverter.file_data
    assert inverter.frames_served == [0, 1, 2]  # 20 bytes over 8-byte frames


async def test_read_file_rejects_a_bad_crc(pdu_unit: PduUnit, inverter: FakeInverter) -> None:
    await session.login(pdu_unit, "installer", inverter.password)
    real_respond = inverter.respond

    def corrupt(pdu: Any) -> bytes:
        if isinstance(pdu, CompleteUploadPDU):
            return struct.pack(">BBBBH", 0x41, 0x0C, 3, FILE_TYPE, 0xDEAD)
        return real_respond(pdu)

    inverter.respond = corrupt  # type: ignore[method-assign]

    with pytest.raises(ReadException, match="does not match expected value"):
        await session.read_file(pdu_unit, FILE_TYPE)


async def test_read_file_without_a_session_is_a_permission_error(pdu_unit: PduUnit) -> None:
    """Huawei's private 0x80 exception code becomes a typed error, not a bare code."""
    with pytest.raises(PermissionDeniedError):
        await session.read_file(pdu_unit, FILE_TYPE)


async def test_heartbeat_writes_the_keepalive_register(pdu_unit: PduUnit) -> None:
    await pdu_unit._ensure_connected()
    assert await session.heartbeat(pdu_unit) is True
    assert pdu_unit.holding[session.HEARTBEAT_REGISTER] == 1


async def test_heartbeat_reports_a_refusal_rather_than_raising(pdu_unit: PduUnit) -> None:
    await pdu_unit._ensure_connected()
    pdu_unit.fail_write(session.HEARTBEAT_REGISTER, IllegalDataAddressError())

    assert await session.heartbeat(pdu_unit) is False


async def test_login_needs_a_backend_that_can_send_raw_pdus() -> None:
    """A plain ModbusUnit cannot reach function code 0x41, and says so."""
    plain = MockModbusConnection().for_unit(1)

    with pytest.raises(TypeError, match="private function code 0x41"):
        await session.login(plain, "installer", "hunter2")
