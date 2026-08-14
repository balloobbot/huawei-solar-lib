"""Base for classes that represent a single Huawei Solar device."""

from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, NamedTuple, Self

from modbus_connection import (
    ExceptionCode,
    ModbusConnectionError,
    ModbusError,
    ModbusTimeoutError,
)

from huawei_solar import session
from huawei_solar.exceptions import (
    InvalidCredentials,
    PermissionDeniedError,
    ReadException,
    WriteException,
)
from huawei_solar.registry import REGISTER_LOCATIONS

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from modbus_connection import ModbusUnit

    from huawei_solar.components.base import HuaweiComponent
    from huawei_solar.registry import RegisterLocation

_LOGGER = logging.getLogger(__name__)

HEARTBEAT_INTERVAL = 15

#: Written back with the value it already holds, to find out whether this
#: connection is allowed to write at all.
WRITE_TEST_REGISTER = "time_zone"

#: Different firmwares answer with one or the other for the same "this register
#: is not here" condition, so probing has to treat both as "the device says no".
ABSENT_CODES = {ExceptionCode.ILLEGAL_DATA_VALUE, ExceptionCode.ILLEGAL_DATA_ADDRESS}


@contextmanager
def suppress_absent_register(what: str) -> Iterator[None]:
    """Swallow the device saying "no such register", but nothing else.

    A probe for an optional sub-system may only conclude "absent" from the
    device refusing the address. Anything else — busy, garbled, timed out —
    propagates, so setup fails and runs again later instead of latching the
    sub-system away for the lifetime of this device object.
    """
    try:
        yield
    except ReadException as err:
        if err.modbus_exception_code not in ABSENT_CODES:
            raise
        _LOGGER.debug("%s is not available on this device", what)


@dataclass(frozen=True)
class UpdateReport:
    """What one batch update read, by component.

    A component whose read failed contributes nothing: its registers are absent
    from ``values`` and the error that failed it is listed under the component's
    name, while every other component still refreshed. A device that answered
    nothing at all is never reported — the update raises instead, because that
    is indistinguishable from a device that is gone.

    The errors are ``modbus_connection``'s own: they are handed on as they were
    raised rather than translated, so a caller can tell a refusal from a timeout
    without parsing a message.
    """

    values: dict[str, Any]
    updated: set[str]
    failed: dict[str, ModbusError]

    @property
    def complete(self) -> bool:
        """Whether every component in the poll refreshed."""
        return not self.failed


def _instance_key(location: RegisterLocation) -> tuple[type[HuaweiComponent], int]:
    """Return the component instance a register lives on: its class and its index."""
    return (location.component, location.instance or 1)


def _component_name(location: RegisterLocation) -> str:
    """Return the name a poll reports the component instance under."""
    if location.instance is None:
        return location.component.__name__
    return f"{location.component.__name__}[{location.instance}]"


class _PollUnit(NamedTuple):
    """One component instance and the registers it answers for.

    The unit a poll is contained at: it either refreshes whole or fails whole,
    because a component reads all of its blocks or none of them.
    """

    component: HuaweiComponent
    names: list[str]

    def first_address(self) -> int:
        """Return the lowest address this unit reads."""
        return min(self.component.resolved_fields[REGISTER_LOCATIONS[name].field].address for name in self.names)

    def values(self) -> dict[str, Any]:
        """Return the values this unit just read, by register name."""
        return {name: getattr(self.component, REGISTER_LOCATIONS[name].field) for name in self.names}


class _Poll:
    """One shaped read: the components covering a set of registers.

    A component is narrowed to the fields the caller asked for, so a Home
    Assistant install with half its entities disabled does not read the other
    half. ``restrict_fields`` only ever narrows, so a changed set of registers
    builds fresh components rather than widening these.
    """

    def __init__(self, unit: ModbusUnit, names: Iterable[str]) -> None:
        """Build the components covering ``names``, one poll unit each."""
        self.names = list(names)
        wanted: dict[str, list[str]] = {}
        keys: dict[str, tuple[type[HuaweiComponent], int]] = {}
        for name in self.names:
            location = REGISTER_LOCATIONS[name]
            component_name = _component_name(location)
            keys[component_name] = _instance_key(location)
            wanted.setdefault(component_name, []).append(name)

        units: dict[str, _PollUnit] = {}
        for component_name, register_names in wanted.items():
            component_class, index = keys[component_name]
            component = component_class(unit, index)
            component.restrict_fields({REGISTER_LOCATIONS[name].field for name in register_names})
            units[component_name] = _PollUnit(component, register_names)

        # Read low addresses first, so the requests do not come out in whichever
        # order the caller happened to list its registers.
        self.units = dict(sorted(units.items(), key=lambda item: item[1].first_address()))

    def matches(self, names: Iterable[str]) -> bool:
        """Whether this poll already covers exactly ``names``."""
        return set(self.names) == set(names)


class HuaweiSolarDevice(ABC):
    """A higher-level interface making it easier to interact with a Huawei Solar device."""

    model_name: str
    serial_number: str
    update_lock: asyncio.Lock
    primary_device: HuaweiSolarDevice | None = None

    def __init__(
        self,
        unit: ModbusUnit,
        model_name: str,
        *,
        unit_id: int = 0,
        primary_device: HuaweiSolarDevice | None = None,
    ) -> None:
        """DO NOT USE THIS CONSTRUCTOR DIRECTLY. Use create() method instead."""
        self.unit = unit
        # A ModbusUnit does not say which unit id it addresses, and consumers key
        # devices by it, so it is carried alongside the handle.
        self.unit_id = unit_id
        self.model_name = model_name
        # Sub-devices share the primary device's lock: they share its Modbus
        # link, and the inverter answers one conversation at a time.
        self.update_lock = primary_device.update_lock if primary_device else asyncio.Lock()
        self.primary_device = primary_device
        self._poll: _Poll | None = None
        self._writable: dict[tuple[type[HuaweiComponent], int], HuaweiComponent] = {}
        # Every register this device has actually read, poll or setup probe.
        # A raw dump is built from it, so the identity registers read once at
        # setup are in it as well.
        self._read_registers: set[str] = set()

    @classmethod
    async def create(
        cls,
        unit: ModbusUnit,
        *,
        model_name: str,
        unit_id: int = 0,
        primary_device: HuaweiSolarDevice | None = None,
    ) -> Self:
        """Create instance with the necessary information."""
        device = cls(unit, model_name, unit_id=unit_id, primary_device=primary_device)
        await device._populate_additional_fields()
        return device

    @abstractmethod
    async def _populate_additional_fields(self) -> None:
        """Allow subclass to populate additional fields with information."""

    @classmethod
    @abstractmethod
    def supports_device(cls, model_name: str) -> bool:
        """Check if this class support the given device."""

    # -- reading -------------------------------------------------------------

    def _handle_batch_read_error(  # noqa: B027
        self,
        _queried_register_names: list[str],
        _exc: ModbusError,
    ) -> None:
        """Note that one component of a batch update failed to read.

        The failure is already contained by the time this is called — the rest
        of the poll still runs — so an implementation records what it learns
        from it and returns.
        """

    def _detect_state_changes(self, new_values: dict[str, Any]) -> None:  # noqa: B027
        """Update state based on the result of a batch_update query.

        Used by subclasses to detect important changes.
        """

    async def _filter_registers(self, register_names: list[str]) -> list[str]:
        """Filter registers being requested in batch_update.

        Used by subclasses to prevent read-errors in certain cases.
        """
        return register_names

    def _transform_register_values(self, register_name: str, value: Any) -> Any:  # noqa: ANN401, ARG002
        """Optionally transform the value of a register before returning it."""
        return value

    async def batch_update(self, register_names: list[str]) -> dict[str, Any]:
        """Read every register in ``register_names`` in as few requests as the device allows.

        Registers whose component failed to read are absent from the result.
        Use :meth:`batch_update_report` to learn which those were, and why.
        """
        return (await self.batch_update_report(register_names)).values

    async def batch_update_report(self, register_names: list[str]) -> UpdateReport:
        """Read every register in ``register_names``, one component at a time.

        A component that fails to read does not take the rest of the poll with
        it: its registers stay out of the result while every other component
        still refreshes. Only a device that answered nothing at all raises.
        """
        if unknown := [name for name in register_names if name not in REGISTER_LOCATIONS]:
            _LOGGER.warning("Unknown register name passed to batch_update: %s", ", ".join(unknown))
            register_names = [name for name in register_names if name in REGISTER_LOCATIONS]

        async with self.update_lock:
            wanted = await self._filter_registers(register_names)

            if self._poll is None or not self._poll.matches(wanted):
                self._poll = _Poll(self.unit, wanted)

            _LOGGER.debug("Batch update of the following registers: %s", ", ".join(wanted))

            values: dict[str, Any] = {}
            updated: set[str] = set()
            failed: dict[str, ModbusError] = {}
            for name, poll_unit in self._poll.units.items():
                try:
                    await poll_unit.component.async_update()
                except ModbusConnectionError:
                    with session.translating("read registers"):
                        raise
                except ModbusTimeoutError as err:
                    if not updated and not failed:
                        # Nothing has answered yet, not even a refusal: the device
                        # is silent, and walking the rest costs a timeout each.
                        with session.translating("read registers"):
                            raise
                    failed[name] = err
                    self._handle_batch_read_error(poll_unit.names, err)
                except ModbusError as err:
                    failed[name] = err
                    self._handle_batch_read_error(poll_unit.names, err)
                else:
                    updated.add(name)
                    values.update(poll_unit.values())
                    self._read_registers.update(poll_unit.names)

            if failed and not updated:
                # Nothing came back at all. There is no partial result to report,
                # and the caller cannot tell this apart from a device that is
                # gone, so it goes out the way a failed read always did.
                with session.translating("read registers"):
                    raise next(iter(failed.values()))

            self._detect_state_changes(values)
            return UpdateReport(
                {name: self._transform_register_values(name, value) for name, value in values.items()},
                updated,
                failed,
            )

    async def async_read_raw(self) -> dict[str, dict[int, int | bool]]:
        """Read every register this device reads, undecoded, keyed by space and address.

        For diagnostics: it is what an issue report needs attached, and what the
        mock backend replays. That includes the identity registers read once at
        setup — no poll goes back to them, so walking the last poll alone would
        drop exactly the registers that identify the device.

        A component that will not answer is left out instead of failing the
        dump: a device that is misbehaving is when the dump is worth having.
        Only a dropped link raises.
        """
        async with self.update_lock:
            # Through the same filter a poll goes through: reading the power
            # meter while it is offline makes the inverter close the connection.
            names = await self._filter_registers(sorted(self._read_registers))
            raw: dict[str, dict[int, int | bool]] = {}
            # Components of their own, so a dump does not hand the poll's
            # components new values behind its back.
            for name, poll_unit in _Poll(self.unit, names).units.items():
                try:
                    read = await poll_unit.component.async_read_raw(notify=False)
                except ModbusConnectionError:
                    with session.translating("read registers"):
                        raise
                except ModbusError as err:
                    _LOGGER.debug("%s is not in the raw dump: %s", name, err)
                    continue
                for space, values in read.items():
                    raw.setdefault(space, {}).update(values)
            return raw

    async def get(self, name: str) -> Any:  # noqa: ANN401
        """Get the value of a certain register."""
        return (await self.batch_update([name]))[name]

    async def get_multiple(self, names: list[str]) -> dict[str, Any]:
        """Get the values of several registers.

        All of them: asking for a value and being handed a dict that does not
        have it is worse than being told why. A poll, which has other registers
        to get on with, is the one that tolerates a partial answer.
        """
        report = await self.batch_update_report(names)
        if not report.complete:
            with session.translating("read registers"):
                raise next(iter(report.failed.values()))
        return report.values

    # -- writing -------------------------------------------------------------

    def _component_for_write(self, name: str) -> tuple[HuaweiComponent, str]:
        """Return the component instance to write ``name`` through, and the field name.

        Kept apart from the polling components, which are narrowed to whatever
        is being read and would refuse a write to a field left out of them.
        """
        try:
            location = REGISTER_LOCATIONS[name]
        except KeyError as err:
            msg = f"Invalid register name: {name}"
            raise ValueError(msg) from err

        key = _instance_key(location)
        component = self._writable.get(key)
        if component is None:
            component = self._writable[key] = key[0](self.unit, key[1])
        return component, location.field

    async def set(self, name: str, value: Any) -> bool:  # noqa: ANN401
        """Set a register to a certain value."""
        component, field = self._component_for_write(name)
        try:
            with session.translating(f"write register {name}", failure="write"):
                await component.write(field, value)
        except AttributeError as err:
            msg = f"Register {name} is not writable"
            raise WriteException(msg) from err
        return True

    async def stop(self) -> bool:
        """Stop the device connection."""
        return True


class HuaweiSolarDeviceWithLogin(HuaweiSolarDevice, ABC):
    """A HuaweiSolarDevice that needs a login session for privileged registers."""

    def __init__(
        self,
        unit: ModbusUnit,
        model_name: str,
        *,
        unit_id: int = 0,
        primary_device: HuaweiSolarDevice | None = None,
    ) -> None:
        """Initialize with per-instance lock and login state."""
        super().__init__(unit, model_name, unit_id=unit_id, primary_device=primary_device)
        self.__login_lock = asyncio.Lock()
        self.__heartbeat_enabled = False
        self.__heartbeat_task: asyncio.Task[None] | None = None
        self.__username: str | None = None
        self.__password: str | None = None
        # A dropped link takes the login session with it. The connection
        # re-establishes itself on the next request, so nothing here needs to
        # reconnect — it only has to remember that the session is gone.
        self.__unsubscribe = unit.on_connection_lost(self._forget_session)

    def _forget_session(self) -> None:
        """Note that the login session went away with the connection."""
        if self.__heartbeat_enabled:
            _LOGGER.debug("Connection lost: the login session is gone, will log in again when needed")
        self.__heartbeat_enabled = False

    async def ensure_logged_in(self, *, force: bool = False) -> bool:
        """Log in if the session is not (or no longer) established."""
        async with self.__login_lock:
            if force:
                _LOGGER.debug("Forcefully stopping any heartbeat task (if any is still running)")
                self.stop_heartbeat()

            if self.__username and not self.__heartbeat_enabled:
                _LOGGER.debug("Currently not logged in: logging in now and starting heartbeat")
                if not self.__password:
                    msg = "Password must be set before logging in"
                    raise InvalidCredentials(msg)
                if not await session.login(self.unit, self.__username, self.__password):
                    raise InvalidCredentials

                self.start_heartbeat()

        return True

    async def login(self, username: str, password: str) -> bool:
        """Perform the login-sequence with the provided username/password."""
        async with self.__login_lock:
            if not await session.login(self.unit, username, password):
                raise InvalidCredentials

            # save the correct login credentials
            self.__username = username
            self.__password = password
            self.start_heartbeat()

        return True

    def stop_heartbeat(self) -> None:
        """Stop the running heartbeat task (if any)."""
        self.__heartbeat_enabled = False

        if self.__heartbeat_task:
            self.__heartbeat_task.cancel()

    def start_heartbeat(self) -> None:
        """Start the heartbeat task to stay logged in."""
        if not self.__login_lock.locked():
            msg = "start_heartbeat should only be called from within the login_lock"
            raise RuntimeError(msg)

        if self.__heartbeat_task:
            self.stop_heartbeat()

        async def heartbeat() -> None:
            while self.__heartbeat_enabled:
                self.__heartbeat_enabled = await session.heartbeat(self.unit)
                await asyncio.sleep(HEARTBEAT_INTERVAL)

        self.__heartbeat_enabled = True
        self.__heartbeat_task = asyncio.create_task(heartbeat())

    async def stop(self) -> bool:
        """Stop the device."""
        self.stop_heartbeat()
        self.__unsubscribe()

        return await super().stop()

    async def read_file(self, file_type: int, customized_data: bytes | None = None) -> bytes:
        """Read a file from the device, logging in again if the session lapsed."""
        logged_in = await self.ensure_logged_in()

        if not logged_in:
            _LOGGER.warning("Could not login, reading file %x will probably fail", file_type)

        try:
            async with self.update_lock:
                return await session.read_file(self.unit, file_type, customized_data)
        except PermissionDeniedError:
            if not self.__username:
                raise  # no credentials available, pass the permission error on

            if not await self.ensure_logged_in(force=True):
                _LOGGER.exception("Could not login to read file %x", file_type)
                raise

            async with self.update_lock:
                return await session.read_file(self.unit, file_type, customized_data)

    ############################
    # Everything write-related #
    ############################

    async def has_write_permission(self) -> bool:
        """Check write permission by writing the time zone back unchanged."""
        try:
            await super().set(WRITE_TEST_REGISTER, await self.get(WRITE_TEST_REGISTER))
        except (PermissionDeniedError, WriteException):
            # Not only PermissionDeniedError: some firmware versions answer a
            # write they will not allow with a plain server-device-failure.
            # cfr. https://github.com/wlcrs/huawei-solar-lib/issues/28
            return False
        else:
            return True

    async def set(self, name: str, value: Any) -> bool:  # noqa: ANN401
        """Set a register to a certain value."""
        logged_in = await self.ensure_logged_in()  # we must login again before trying to set the value

        if not logged_in:
            _LOGGER.warning("Could not login, setting %s will probably fail", name)

        if self.__heartbeat_enabled:
            await session.heartbeat(self.unit)

        try:
            return await super().set(name, value)
        except PermissionDeniedError:
            if not self.__username:
                raise  # no credentials available, pass the permission error on

            if not await self.ensure_logged_in(force=True):
                _LOGGER.exception("Could not login to set %s", name)
                raise

            # Force a heartbeat first when connected with username/password credentials
            await session.heartbeat(self.unit)

            return await super().set(name, value)
