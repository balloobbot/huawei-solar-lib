"""Huawei-flavoured register fields for ``modbus_connection``'s model layer.

Most of Huawei's map is ordinary scaled integers and strings, which
``modbus_connection.model`` covers directly. What it does not cover, and what
therefore lives here:

* **Gain is a divisor.** Huawei publishes ``gain`` and the value is
  ``raw / gain``; ``modbus_connection`` scales by multiplication.
  :class:`GainField` divides instead, which the register tables quote directly.
* **Strings carry garbage past the first NUL.** Huawei pads with whatever was
  in the buffer, and the text is UTF-8, not ASCII. :class:`HuaweiStringField`
  truncates at the first NUL and decodes leniently.
* **Timestamps are naive.** The inverter reports a local-time epoch with no
  offset; the device layer applies its own time zone and DST correction later.
* **Four packed period tables** — time-of-use, forcible charge/discharge and
  peak-shaving schedules — that pack a count followed by a byte-packed array
  spanning dozens of registers, with a Python dataclass per entry.
"""

from __future__ import annotations

import struct
from collections.abc import Mapping
from datetime import datetime
from typing import TYPE_CHECKING, Any

from modbus_connection.encode import encode_int
from modbus_connection.model import NumberField, RegisterField

from huawei_solar.exceptions import DecodeError, EncodeError, WriteException
from huawei_solar.periods import (
    CHARGE_DISCHARGE_PERIODS,
    HUAWEI_LUNA2000_TOU_PERIODS,
    LG_RESU_TOU_PERIODS,
    PEAK_SETTING_PERIODS,
    ChargeDischargePeriod,
    ChargeFlag,
    HUAWEI_LUNA2000_TimeOfUsePeriod,
    LG_RESU_TimeOfUsePeriod,
    PeakSettingPeriod,
    days_effective_builder,
    days_effective_parser,
    validate_huawei_luna2000_tou_periods,
    validate_lg_resu_tou_periods,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    from modbus_connection.model import Converter, WriteValidator

# The sentinel each width uses for "no value". Huawei reports the largest
# representable number of the register's own signedness.
INVALID_U16 = 2**16 - 1
INVALID_U32 = 2**32 - 1
INVALID_U64 = 2**64 - 1
INVALID_I16 = 2**15 - 1
INVALID_I32 = 2**31 - 1
INVALID_I64 = 2**63 - 1


def _strict(convert: Converter) -> Callable[[int], Any]:
    """Wrap a converter so an unrecognised value fails the read.

    ``modbus_connection`` treats a value its converter does not recognise as
    missing: it warns once and decodes ``None``. Huawei's library has always
    treated it as an error instead, so a firmware reporting a state this
    library does not know about is noticed rather than shown as a blank
    sensor. ``DecodeError`` is not a ``ValueError``, so it travels out through
    the model layer untouched.
    """

    def apply(raw: int) -> Any:
        try:
            return convert[raw] if isinstance(convert, Mapping) else convert(raw)
        except (KeyError, ValueError) as err:
            msg = f"Failed to decode value: {err}"
            raise DecodeError(msg) from err

    return apply


class GainField(NumberField[Any]):
    """A Huawei numeric register: a raw integer over a published gain.

    Huawei quotes a ``gain`` and the value is ``raw / gain``, whereas
    ``modbus_connection`` scales by multiplying by a ``scale``. Passing
    ``1 / gain`` would be close but not equal — for a 64-bit energy counter over
    a gain of 1000 the two differ in the last bits — so the division is done
    here and the model layer is left with a scale of 1.
    """

    def __init__(self, address: int, *, gain: float = 1, **kwargs: Any) -> None:
        """Create a field over a register published with ``gain``."""
        super().__init__(address, **kwargs)
        self.gain = gain

    def decode(self, words: list[int], scale_exponent: int | None = None) -> Any:
        """Decode the register and divide out its gain."""
        value = super().decode(words, scale_exponent)
        if self.gain == 1 or value is None or self.convert is not None:
            return value
        return value / self.gain

    def encode(self, value: Any, scale_exponent: int | None = None) -> list[int]:
        """Encode a value back through its gain."""
        if isinstance(value, (int, float)):
            raw = int(value * self.gain)
        elif value is None:
            if self.nan is None:
                msg = "This register does not support writing None."
                raise WriteException(msg)
            raw = next(iter(self.nan))
        else:
            msg = f"Unsupported type: {type(value)}."
            raise WriteException(msg)
        # encode_int accepts anything that fits the register's *unsigned* range,
        # so a signed register would silently wrap a value the device would
        # read back as negative. Reject it the way packing the old struct format
        # did, but as a typed error rather than a struct.error escaping.
        bits = 16 * self.count
        low, high = (-(1 << (bits - 1)), (1 << (bits - 1)) - 1) if self.signed else (0, (1 << bits) - 1)
        if not low <= raw <= high and raw not in (self.nan or ()):
            msg = f"Value {value} encodes to {raw}, outside the range {low}..{high} of this register"
            raise WriteException(msg)
        return encode_int(raw, count=self.count)


def number(  # noqa: PLR0913 — one parameter per column of Huawei's register table
    address: int,
    *,
    count: int,
    signed: bool,
    nan: int | Iterable[int] | None,
    gain: float = 1,
    unit: str | None = None,
    convert: Converter | None = None,
    writable: bool | WriteValidator = False,
    stride: int = 0,
    field_class: type[GainField] = GainField,
) -> GainField:
    """Create a numeric field from a Huawei register description."""
    if convert is not None and gain != 1:
        msg = f"register {address}: a converted register cannot also have a gain"
        raise ValueError(msg)
    return field_class(
        address,
        gain=gain,
        count=count,
        signed=signed,
        nan=nan,
        unit=unit,
        convert=_strict(convert) if convert is not None else None,
        writable=writable,
        stride=stride,
    )


def u16(address: int, **kwargs: Any) -> GainField:
    """Create a field for an unsigned 16-bit Huawei register."""
    kwargs.setdefault("nan", INVALID_U16)
    return number(address, count=1, signed=False, **kwargs)


def u32(address: int, **kwargs: Any) -> GainField:
    """Create a field for an unsigned 32-bit Huawei register."""
    kwargs.setdefault("nan", INVALID_U32)
    return number(address, count=2, signed=False, **kwargs)


def u64(address: int, **kwargs: Any) -> GainField:
    """Create a field for an unsigned 64-bit Huawei register."""
    kwargs.setdefault("nan", INVALID_U64)
    return number(address, count=4, signed=False, **kwargs)


def i16(address: int, **kwargs: Any) -> GainField:
    """Create a field for a signed 16-bit Huawei register."""
    kwargs.setdefault("nan", INVALID_I16)
    return number(address, count=1, signed=True, **kwargs)


def i32(address: int, **kwargs: Any) -> GainField:
    """Create a field for a signed 32-bit Huawei register."""
    kwargs.setdefault("nan", INVALID_I32)
    return number(address, count=2, signed=True, **kwargs)


def i64(address: int, **kwargs: Any) -> GainField:
    """Create a field for a signed 64-bit Huawei register."""
    kwargs.setdefault("nan", INVALID_I64)
    return number(address, count=4, signed=True, **kwargs)


class AbsoluteValueField(GainField):
    """A signed register whose value is always meant to be positive.

    Some firmwares report these as negative. cfr.
    https://github.com/wlcrs/huawei_solar/issues/54
    """

    def decode(self, words: list[int], scale_exponent: int | None = None) -> Any:
        """Decode and drop the sign."""
        value = super().decode(words, scale_exponent)
        return None if value is None else abs(value)


def i32_absolute(address: int, **kwargs: Any) -> AbsoluteValueField:
    """Create a field for a signed 32-bit register reported as its absolute value."""
    kwargs.setdefault("nan", INVALID_I32)
    field = number(address, count=2, signed=True, field_class=AbsoluteValueField, **kwargs)
    assert isinstance(field, AbsoluteValueField)
    return field


def bytes_to_string(value: bytes) -> str:
    """Decode Huawei text: UTF-8 up to the first NUL, garbage after it.

    Huawei pads the tail of a string with leftover buffer content rather than
    zeroes, so everything from the first NUL on is dropped rather than stripped.
    """
    null_byte_index = value.find(b"\x00")
    if null_byte_index != -1:
        value = value[:null_byte_index]
    return value.decode("utf-8", errors="backslashreplace")


class HuaweiStringField(RegisterField[str]):
    """A UTF-8 string register, truncated at the first NUL.

    Huawei pads the tail of a string register with leftover buffer content
    rather than zeroes, so everything from the first NUL on is garbage and must
    be dropped rather than stripped.
    """

    def decode(self, words: list[int], scale_exponent: int | None = None) -> str:
        """Decode the registers as UTF-8 up to the first NUL."""
        return bytes_to_string(b"".join((word & 0xFFFF).to_bytes(2, "big") for word in words))

    def encode(self, value: Any, scale_exponent: int | None = None) -> list[int]:
        """Encode a string, NUL-padded to this field's register count."""
        raw = str(value).encode("utf-8")[: self.count * 2].ljust(self.count * 2, b"\x00")
        return [int.from_bytes(raw[i : i + 2], "big") for i in range(0, len(raw), 2)]


def text(
    address: int,
    count: int,
    *,
    writable: bool | WriteValidator = False,
    stride: int = 0,
) -> HuaweiStringField:
    """Create a field for a Huawei string spanning ``count`` registers."""
    return HuaweiStringField(address, count=count, writable=writable, stride=stride)


class TimestampField(GainField):
    """A Unix epoch reported in the device's own local time.

    The inverter gives no offset, so the value is decoded naive here and the
    device layer shifts it once it knows the configured time zone and whether
    DST is in effect.
    """

    def decode(self, words: list[int], scale_exponent: int | None = None) -> datetime | None:
        """Decode the epoch as a naive datetime."""
        value = super().decode(words, scale_exponent)
        if value is None:
            return None
        return datetime.fromtimestamp(value)  # noqa: DTZ006


def timestamp(address: int, *, writable: bool | WriteValidator = False) -> TimestampField:
    """Create a field for a Huawei timestamp register."""
    return TimestampField(
        address,
        count=2,
        signed=False,
        nan=INVALID_U32,
        writable=writable,
    )


class _PackedPeriodsField[T](RegisterField[list[T]]):
    """A count-prefixed, byte-packed table of schedule entries.

    The wire layout is one count register followed by a fixed-size array of
    ``max_periods`` entries. Entries are packed by *byte*, not by register, so
    a table is decoded from the block's bytes rather than register by register.
    Trailing entries past the count are padding and are ignored.
    """

    entry_format: str
    max_periods: int

    def _unpack(self, words: list[int]) -> tuple[int, list[tuple[Any, ...]]]:
        raw = b"".join((word & 0xFFFF).to_bytes(2, "big") for word in words)
        entry = struct.Struct(f">{self.entry_format}")
        (count,) = struct.unpack_from(">H", raw, 0)
        entries = [entry.unpack_from(raw, 2 + idx * entry.size) for idx in range(self.max_periods)]
        return count, entries

    def _pack(self, count: int, entries: list[tuple[Any, ...]]) -> list[int]:
        entry = struct.Struct(f">{self.entry_format}")
        raw = struct.pack(">H", count)
        for values in entries:
            raw += entry.pack(*values)
        raw += bytes(entry.size * (self.max_periods - len(entries)))
        return [int.from_bytes(raw[i : i + 2], "big") for i in range(0, len(raw), 2)]


class LgResuTimeOfUseField(_PackedPeriodsField[LG_RESU_TimeOfUsePeriod]):
    """The LG RESU time-of-use price schedule."""

    entry_format = "HHI"
    max_periods = LG_RESU_TOU_PERIODS

    def decode(self, words: list[int], scale_exponent: int | None = None) -> list[LG_RESU_TimeOfUsePeriod]:
        """Decode the time-of-use table."""
        count, entries = self._unpack(words)
        if count > self.max_periods:
            msg = f"Device reported {count} TOU periods, but the maximum is {self.max_periods}"
            raise DecodeError(msg)
        return [LG_RESU_TimeOfUsePeriod(start, end, price / 1000) for start, end, price in entries[:count]]

    def encode(self, value: Any, scale_exponent: int | None = None) -> list[int]:
        """Encode the time-of-use table."""
        periods: list[LG_RESU_TimeOfUsePeriod] = list(value)
        validate_lg_resu_tou_periods(periods)
        return self._pack(
            len(periods),
            [(p.start_time, p.end_time, int(p.electricity_price * 1000)) for p in periods],
        )


class HuaweiLuna2000TimeOfUseField(_PackedPeriodsField[HUAWEI_LUNA2000_TimeOfUsePeriod]):
    """The Huawei LUNA2000 time-of-use schedule."""

    entry_format = "HHBB"
    max_periods = HUAWEI_LUNA2000_TOU_PERIODS

    def decode(self, words: list[int], scale_exponent: int | None = None) -> list[HUAWEI_LUNA2000_TimeOfUsePeriod]:
        """Decode the time-of-use table."""
        count, entries = self._unpack(words)
        if count > self.max_periods:
            msg = f"Device reported {count} TOU periods, but the maximum is {self.max_periods}"
            raise DecodeError(msg)
        return [
            HUAWEI_LUNA2000_TimeOfUsePeriod(start, end, ChargeFlag(charge), days_effective_parser(days))
            for start, end, charge, days in entries[:count]
        ]

    def encode(self, value: Any, scale_exponent: int | None = None) -> list[int]:
        """Encode the time-of-use table."""
        periods: list[HUAWEI_LUNA2000_TimeOfUsePeriod] = list(value)
        validate_huawei_luna2000_tou_periods(periods)
        return self._pack(
            len(periods),
            [(p.start_time, p.end_time, int(p.charge_flag), days_effective_builder(p.days_effective)) for p in periods],
        )


class ChargeDischargePeriodsField(_PackedPeriodsField[ChargeDischargePeriod]):
    """The forcible charge/discharge schedule."""

    entry_format = "HHI"
    max_periods = CHARGE_DISCHARGE_PERIODS

    def decode(self, words: list[int], scale_exponent: int | None = None) -> list[ChargeDischargePeriod]:
        """Decode the charge/discharge table."""
        count, entries = self._unpack(words)
        if count > self.max_periods:
            msg = f"Device reported {count} charge/discharge periods, but the maximum is {self.max_periods}"
            raise DecodeError(msg)
        return [ChargeDischargePeriod(start, end, power) for start, end, power in entries[:count]]

    def encode(self, value: Any, scale_exponent: int | None = None) -> list[int]:
        """Encode the charge/discharge table."""
        periods: list[ChargeDischargePeriod] = list(value)
        if len(periods) > self.max_periods:
            msg = f"Too many charge/discharge periods: got {len(periods)}, maximum is {self.max_periods}"
            raise EncodeError(msg)
        return self._pack(len(periods), [(p.start_time, p.end_time, p.power) for p in periods])


class PeakSettingPeriodsField(_PackedPeriodsField[PeakSettingPeriod]):
    """The peak-shaving schedule.

    Unlike the other tables this one tolerates a count larger than the array
    and silently drops entries that are empty (equal start and end, or no days
    selected), because firmwares have been seen reporting both.
    """

    entry_format = "HHIB"
    max_periods = PEAK_SETTING_PERIODS

    def decode(self, words: list[int], scale_exponent: int | None = None) -> list[PeakSettingPeriod]:
        """Decode the peak-shaving table."""
        count, entries = self._unpack(words)
        return [
            PeakSettingPeriod(start, end, peak, days_effective_parser(days))
            for start, end, peak, days in entries[: min(count, self.max_periods)]
            if start != end and days != 0
        ]

    def encode(self, value: Any, scale_exponent: int | None = None) -> list[int]:
        """Encode the peak-shaving table.

        Deliberately unvalidated: callers reach for
        :func:`~huawei_solar.periods.validate_peak_setting_periods` themselves,
        as they always have.
        """
        periods: list[PeakSettingPeriod] = list(value)[: self.max_periods]
        return self._pack(
            len(periods),
            [(p.start_time, p.end_time, p.power, days_effective_builder(p.days_effective)) for p in periods],
        )
