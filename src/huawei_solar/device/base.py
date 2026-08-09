"""Base for classes that represent a single Huawei Solar device."""

from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Self

from modbus_connection import ModbusExceptionError
from modbus_connection.model import ComponentGroup

from huawei_solar import session
from huawei_solar.exceptions import (
    HuaweiSolarException,
    InvalidCredentials,
    PermissionDeniedError,
    WriteException,
)
from huawei_solar.registry import REGISTER_LOCATIONS

if TYPE_CHECKING:
    from collections.abc import Iterable

    from modbus_connection import ModbusUnit

    from huawei_solar.components.base import HuaweiComponent
    from huawei_solar.registry import RegisterLocation

_LOGGER = logging.getLogger(__name__)

HEARTBEAT_INTERVAL = 15

#: Written back with the value it already holds, to find out whether this
#: connection is allowed to write at all.
WRITE_TEST_REGISTER = "time_zone"


def _instance_key(location: RegisterLocation) -> tuple[type[HuaweiComponent], int]:
    """Return the component instance a register lives on: its class and its index."""
    return (location.component, location.instance or 1)


class _Poll:
    """One shaped read: the components covering a set of registers, pooled.

    A component is narrowed to the fields the caller asked for, so a Home
    Assistant install with half its entities disabled does not read the other
    half. ``restrict_fields`` only ever narrows, so a changed set of registers
    builds fresh components rather than widening these.
    """

    def __init__(self, unit: ModbusUnit, names: Iterable[str]) -> None:
        """Build the components covering ``names`` and pool them into one group."""
        self.names = list(names)
        wanted: dict[tuple[type[HuaweiComponent], int], set[str]] = {}
        for name in self.names:
            location = REGISTER_LOCATIONS[name]
            wanted.setdefault(_instance_key(location), set()).add(location.field)

        self._components: dict[tuple[type[HuaweiComponent], int], HuaweiComponent] = {}
        for (component_class, index), fields in wanted.items():
            component = component_class(unit, index)
            component.restrict_fields(fields)
            # restrict_fields narrows the component's readable ranges by
            # *address*, to keep a device's declared map honest. Huawei names
            # three registers twice — 32066 is grid_voltage on a single-phase
            # inverter and line_voltage_A_B on a three-phase one — so dropping
            # one alias marks the address its twin still reads as unreadable,
            # splitting the block around a register that is being read anyway.
            # None of these components declare ranges, so dropping them puts
            # planning back on gaps over exactly the fields that were kept.
            component.register_ranges = None
            self._components[(component_class, index)] = component

        self._group = ComponentGroup(unit, self._components.values())

    def matches(self, names: Iterable[str]) -> bool:
        """Whether this poll already covers exactly ``names``."""
        return set(self.names) == set(names)

    def covering(self, address: int, count: int) -> list[str]:
        """Return the register names a block read at ``address`` was covering."""
        covered = range(address, address + count)
        found = []
        for name in self.names:
            location = REGISTER_LOCATIONS[name]
            field = location.definition()
            start = field.address + field.stride * ((location.instance or 1) - 1)
            if start in covered or (start + field.count - 1) in covered:
                found.append(name)
        return found

    async def read(self) -> dict[str, Any]:
        """Read every component in one pooled pass and return the values by name."""
        await self._group.async_update()
        values = {}
        for name in self.names:
            location = REGISTER_LOCATIONS[name]
            values[name] = getattr(self._components[_instance_key(location)], location.field)
        return values


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
        primary_device: HuaweiSolarDevice | None = None,
    ) -> None:
        """DO NOT USE THIS CONSTRUCTOR DIRECTLY. Use create() method instead."""
        self.unit = unit
        self.model_name = model_name
        # Sub-devices share the primary device's lock: they share its Modbus
        # link, and the inverter answers one conversation at a time.
        self.update_lock = primary_device.update_lock if primary_device else asyncio.Lock()
        self.primary_device = primary_device
        self._poll: _Poll | None = None
        self._writable: dict[tuple[type[HuaweiComponent], int], HuaweiComponent] = {}

    @classmethod
    async def create(
        cls,
        unit: ModbusUnit,
        *,
        model_name: str,
        primary_device: HuaweiSolarDevice | None = None,
    ) -> Self:
        """Create instance with the necessary information."""
        device = cls(unit, model_name, primary_device=primary_device)
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

    def _handle_batch_read_error(
        self,
        _queried_register_names: list[str],
        exc: HuaweiSolarException,
    ) -> None:
        """Handle read errors in batch_update."""
        raise exc

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
        """Read every register in ``register_names`` in as few requests as the device allows."""
        if unknown := [name for name in register_names if name not in REGISTER_LOCATIONS]:
            _LOGGER.warning("Unknown register name passed to batch_update: %s", ", ".join(unknown))
            register_names = [name for name in register_names if name in REGISTER_LOCATIONS]

        async with self.update_lock:
            wanted = await self._filter_registers(register_names)

            if self._poll is None or not self._poll.matches(wanted):
                self._poll = _Poll(self.unit, wanted)

            _LOGGER.debug("Batch update of the following registers: %s", ", ".join(wanted))

            try:
                with session.translating("read registers"):
                    values = await self._poll.read()
            except HuaweiSolarException as exc:
                self._handle_batch_read_error(self._failed_registers(exc, wanted), exc)
                values = {}

            self._detect_state_changes(values)
            return {name: self._transform_register_values(name, value) for name, value in values.items()}

    def _failed_registers(self, exc: Exception, fallback: list[str]) -> list[str]:
        """Which registers a failed read was after.

        A refused block read names the block it was refused, so the registers it
        was covering can be recovered; anything else took the whole poll down.
        """
        cause = exc.__cause__
        if isinstance(cause, ModbusExceptionError) and cause.block is not None and self._poll is not None:
            return self._poll.covering(cause.block.address, cause.block.count)
        return fallback

    async def get(self, name: str) -> Any:  # noqa: ANN401
        """Get the value of a certain register."""
        return (await self.batch_update([name]))[name]

    async def get_multiple(self, names: list[str]) -> dict[str, Any]:
        """Get the values of several registers."""
        return await self.batch_update(names)

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
        primary_device: HuaweiSolarDevice | None = None,
    ) -> None:
        """Initialize with per-instance lock and login state."""
        super().__init__(unit, model_name, primary_device=primary_device)
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
