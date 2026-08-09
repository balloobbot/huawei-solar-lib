"""Schedule entries carried by Huawei's packed period registers.

The dataclasses, the day-of-week bitmask helpers and the validators live here,
separate from the register fields in :mod:`huawei_solar.fields` that read and
write them, because they are plain data a caller constructs and inspects.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from huawei_solar.exceptions import PeakPeriodsValidationError, TimeOfUsePeriodsException

LG_RESU_TOU_PERIODS = 10
HUAWEI_LUNA2000_TOU_PERIODS = 14
CHARGE_DISCHARGE_PERIODS = 10
PEAK_SETTING_PERIODS = 14

MINUTES_PER_DAY = 24 * 60
DAYS_PER_WEEK = 7


@dataclass(frozen=True, slots=True)
class LG_RESU_TimeOfUsePeriod:
    """Time of use period of LG RESU."""

    start_time: int  # minutes since midnight
    end_time: int  # minutes since midnight
    electricity_price: float


class ChargeFlag(IntEnum):
    """Charge Flag."""

    CHARGE = 0
    DISCHARGE = 1


@dataclass(frozen=True, slots=True)
class HUAWEI_LUNA2000_TimeOfUsePeriod:
    """Time of use period of Huawei LUNA2000."""

    start_time: int  # minutes since midnight
    end_time: int  # minutes since midnight
    charge_flag: ChargeFlag
    days_effective: tuple[bool, bool, bool, bool, bool, bool, bool]  # Sunday to Saturday


@dataclass(frozen=True, slots=True)
class ChargeDischargePeriod:
    """Charge or Discharge Period."""

    start_time: int  # minutes since midnight
    end_time: int  # minutes since midnight
    power: int  # power in watts


@dataclass(frozen=True, slots=True)
class PeakSettingPeriod:
    """Peak Setting Period."""

    start_time: int  # minutes since midnight
    end_time: int  # minutes since midnight
    power: int  # power in watts
    days_effective: tuple[bool, bool, bool, bool, bool, bool, bool]  # Sunday to Saturday


def days_effective_builder(days_tuple: tuple[bool, bool, bool, bool, bool, bool, bool]) -> int:
    """Pack a Sunday-to-Saturday tuple into a day-of-week bitmask."""
    result = 0
    mask = 0x1
    for i in range(DAYS_PER_WEEK):
        if days_tuple[i]:
            result += mask
        mask = mask << 1

    return result


def days_effective_parser(value: int) -> tuple[bool, bool, bool, bool, bool, bool, bool]:
    """Unpack a day-of-week bitmask into a Sunday-to-Saturday tuple."""
    result = []
    mask = 0x1
    for _ in range(DAYS_PER_WEEK):
        result.append((value & mask) != 0)
        mask = mask << 1

    return tuple(result)  # type: ignore[return-value]


def _validate_period_bounds(period: LG_RESU_TimeOfUsePeriod | HUAWEI_LUNA2000_TimeOfUsePeriod) -> None:
    """Check one period sits inside a single day and runs forwards."""
    if period.start_time < 0 or period.end_time < 0:
        msg = "TOU period is invalid (Below zero)"
        raise TimeOfUsePeriodsException(msg)
    if period.start_time > MINUTES_PER_DAY or period.end_time > MINUTES_PER_DAY:
        msg = "TOU period is invalid (Spans over more than one day)"
        raise TimeOfUsePeriodsException(msg)
    if period.start_time >= period.end_time:
        msg = "TOU period is invalid (start-time is greater than end-time)"
        raise TimeOfUsePeriodsException(msg)


def _raise_on_overlap[T: (LG_RESU_TimeOfUsePeriod, HUAWEI_LUNA2000_TimeOfUsePeriod)](periods: list[T]) -> None:
    """Raise if any two periods in ``periods`` overlap."""
    ordered = sorted(periods, key=lambda a: a.start_time)
    for idx in range(1, len(ordered)):
        current = ordered[idx]
        previous = ordered[idx - 1]
        if (
            previous.start_time <= current.start_time < previous.end_time
            or previous.start_time < current.end_time <= previous.end_time
        ):
            msg = "TOU periods are overlapping"
            raise TimeOfUsePeriodsException(msg)


def validate_lg_resu_tou_periods(periods: list[LG_RESU_TimeOfUsePeriod]) -> None:
    """Validate an LG RESU time-of-use schedule."""
    if len(periods) == 0:
        return  # nothing to check

    for period in periods:
        _validate_period_bounds(period)

    _raise_on_overlap(periods)


def validate_huawei_luna2000_tou_periods(periods: list[HUAWEI_LUNA2000_TimeOfUsePeriod]) -> None:
    """Validate a Huawei LUNA2000 time-of-use schedule.

    Periods may overlap as long as they are never active on the same day.
    """
    if len(periods) == 0:
        return  # nothing to check

    for period in periods:
        if not isinstance(period, HUAWEI_LUNA2000_TimeOfUsePeriod):
            msg = "TOU period is of an unexpected type"
            raise TimeOfUsePeriodsException(msg)
        _validate_period_bounds(period)

    if len(periods) > HUAWEI_LUNA2000_TOU_PERIODS:
        msg = f"Too many TOU periods: got {len(periods)}, maximum is {HUAWEI_LUNA2000_TOU_PERIODS}"
        raise TimeOfUsePeriodsException(msg)

    for day_idx in range(DAYS_PER_WEEK):
        _raise_on_overlap([period for period in periods if period.days_effective[day_idx]])


def validate_peak_setting_periods(periods: list[PeakSettingPeriod]) -> None:
    """Validate that a peak-shaving schedule covers every minute of every day."""
    for day_idx in range(DAYS_PER_WEEK):
        active_periods = [period for period in periods if period.days_effective[day_idx]]

        if not active_periods:
            msg = "All days of the week need to be covered"
            raise PeakPeriodsValidationError(msg)

        active_periods.sort(key=lambda a: a.start_time)

        if active_periods[0].start_time != 0:
            msg = "Every day must be covered from 00:00"
            raise PeakPeriodsValidationError(msg)

        for period_idx in range(1, len(active_periods)):
            current_period = active_periods[period_idx]
            prev_period = active_periods[period_idx - 1]
            if current_period.start_time not in (prev_period.end_time, prev_period.end_time + 1):
                msg = "All moments of each day need to be covered"
                raise PeakPeriodsValidationError(msg)

        if active_periods[-1].end_time not in (MINUTES_PER_DAY - 1, MINUTES_PER_DAY):
            msg = "Every day must be covered until 23:59"
            raise PeakPeriodsValidationError(msg)
