from typing import List, Optional, Set
from pydantic import BaseModel
from datetime import date

from .shiftrange import ShiftRange
from .daterange import DateRange
from .daily_shifts import DailyShift
from .common_daysoff import (
    VIETNAM_VICTORY_DAY,
    SOLAR_NEW_YEAR,
    INTERNATIONAL_LABOR_DAY,
    THE_HUNG_KINGS_TEMPLE_FESTIVAL,
    VIETNAM_INDEPENDENT_DAY,
    LUNAR_NEW_YEAR,
    COMMON_WORKDAYS_IN_WEEK,
    COMMON_DAILY_SHIFTS,
    WEEKDAYS,
)

YEAR = MONTH = DAY = int


class ShiftsBuilder(BaseModel):
    """
    `Shifts` configuration for a single `employee/team/firm`. use method `generate_shifts` for generating Shifts based on parsed config.

    To generate shifts, the order of priorities is `special_shifts` > `days_off` > `shifts_daily` + `workdays_weekly`

    :param workdays_weekly: indexes of work days in a week, default is from Monday to Friday [0,1,2,3,4]
    :param shifts_daily: default `Shifts` in a typical workday.
    :param days_off: List of days off, can be *lunar* or *solar* days off
    :param special_shifts: special `Shifts` of a *specific date*, if `None`, that day will have zero shifts.
    """

    workdays_weekly: WEEKDAYS = COMMON_WORKDAYS_IN_WEEK
    shifts_daily: DailyShift = COMMON_DAILY_SHIFTS
    days_off_ranges: List[DateRange] = [
        VIETNAM_VICTORY_DAY,
        VIETNAM_INDEPENDENT_DAY,
        THE_HUNG_KINGS_TEMPLE_FESTIVAL,
        LUNAR_NEW_YEAR,
        SOLAR_NEW_YEAR,
        INTERNATIONAL_LABOR_DAY,
    ]
    special_shifts: ShiftRange = ShiftRange({})

    @property
    def _days_off(self) -> Set[date]:
        return {
            day_off
            for days_off_range in self.days_off_ranges
            for day_off in days_off_range.dates
        }

    def partial_copy(
        self,
        workdays_weekly: WEEKDAYS | None = None,
        shifts_daily: DailyShift | None = None,
        days_off: List[DateRange] | None = None,
        special_shifts: ShiftRange | None = None,
    ) -> "ShiftsBuilder":
        return ShiftsBuilder(
            workdays_weekly=workdays_weekly
            if workdays_weekly
            else self.workdays_weekly,
            shifts_daily=shifts_daily if shifts_daily else self.shifts_daily,
            days_off_ranges=days_off if days_off else self.days_off_ranges,
            special_shifts=special_shifts
            if special_shifts
            else self.special_shifts,
        )

    def add_days_off(
        self, days_off: DateRange, inplace: bool = False
    ) -> Optional["ShiftsBuilder"]:
        if inplace:
            self.days_off_ranges.append(days_off)
            return
        return self.partial_copy(days_off=self.days_off_ranges + [days_off])

    def update_workday_weekly(
        self, workdays: WEEKDAYS, inplace: bool = False
    ) -> Optional["ShiftsBuilder"]:
        if inplace:
            self.workdays_weekly.update(workdays)
            return
        return self.partial_copy(
            workdays_weekly=self.workdays_weekly.union(workdays)
        )

    def update_special_shifts(
        self,
        special_shifts: ShiftRange,
        inplace: bool = False,
    ) -> Optional["ShiftsBuilder"]:
        if inplace:
            self.special_shifts.update(special_shifts)
        return self.partial_copy(special_shifts=special_shifts)

    def set_shifts_daily(
        self, shifts_daily: DailyShift, inplace: bool = False
    ) -> Optional["ShiftsBuilder"]:
        if inplace:
            self.shifts_daily = shifts_daily
            return
        return self.partial_copy(shifts_daily=shifts_daily)

    def set_days_off(
        self, days_off: List[DateRange], inplace: bool = False
    ) -> Optional["ShiftsBuilder"]:
        if inplace:
            self.days_off = days_off
            return
        return self.partial_copy(days_off=days_off)

    # def build_work_days
    def build_shifts_from_daterange(self, daterange: DateRange) -> ShiftRange:
        ...

    def build_shifts_from_hours(
        self,
        hours: int,
    ) -> ShiftRange:
        pass
