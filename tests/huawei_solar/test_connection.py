"""Tests for the retry wrapper on a real ``HuaweiUnit``.

Every other test in this suite drives ``MockModbusUnit``, so nothing else
constructs the unit the library actually ships. These do, over a stand-in for
the tmodbus client the connection would open.
"""

from __future__ import annotations

from typing import Any

import pytest
from huawei_solar.connection import HuaweiModbusConnection, HuaweiUnit
from modbus_connection import ModbusTcpParams
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt

REGISTERS = [11, 22, 33]


def _instant_retry() -> AsyncRetrying:
    """Retry as the shipped policy does, without its backoff, so this does not sleep."""
    return AsyncRetrying(
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(TimeoutError),
        reraise=True,
    )


class FakeClient:
    """Stand in for the tmodbus client, recording the requests that reach it."""

    def __init__(self, timeouts: int = 0) -> None:
        """Set up a client that times out on its first ``timeouts`` reads."""
        self.reads: list[tuple[int, int]] = []
        self.timeouts = timeouts

    def for_unit_id(self, unit_id: int) -> FakeClient:
        """Answer for every unit id; these tests only use one."""
        self.unit_id = unit_id
        return self

    async def read_holding_registers(self, address: int, count: int) -> list[int]:
        """Return registers, once the configured timeouts are used up."""
        self.reads.append((address, count))
        if self.timeouts:
            self.timeouts -= 1
            msg = "no answer"
            raise TimeoutError(msg)
        return REGISTERS[:count]

    async def disconnect(self) -> None:
        """Nothing to tear down."""


class FakeConnection(HuaweiModbusConnection):
    """A Huawei connection whose link is a ``FakeClient``."""

    def __init__(self, client: FakeClient) -> None:
        """Bind this connection to ``client``, without pacing or connect delay."""
        super().__init__(
            ModbusTcpParams(host="fake", port=502),
            message_spacing=0,
            connect_delay=0,
        )
        self.client = client

    async def _connect_client(self) -> Any:
        return self.client


@pytest.fixture
def client() -> FakeClient:
    """Return a client that answers every read."""
    return FakeClient()


async def test_read_holding_registers_returns_the_registers(client: FakeClient) -> None:
    unit = FakeConnection(client).for_unit(1)

    assert isinstance(unit, HuaweiUnit)
    assert await unit.read_holding_registers(30000, 3) == REGISTERS
    assert client.reads == [(30000, 3)]


async def test_a_timed_out_read_is_retried() -> None:
    client = FakeClient(timeouts=1)
    connection = FakeConnection(client)
    connection.retry_factory = _instant_retry

    assert await connection.for_unit(1).read_holding_registers(30000, 3) == REGISTERS
    assert client.reads == [(30000, 3), (30000, 3)]
