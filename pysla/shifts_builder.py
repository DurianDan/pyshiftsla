from typing import Dict, List, Optional, Set
from typing_extensions import Annotated
from pydantic import BaseModel, AfterValidator
from datetime import date
from .daterange import DateRange
from .daily_shifts import DailyShift
from .datetime_utilities import check_valid_weekday
from .common_daysoff import (
    VIETNAM_VICTORY_DAY,
    SOLAR_NEW_YEAR,
    INTERNATIONAL_LABOR_DAY,
    THE_HUNG_KINGS_TEMPLE_FESTIVAL,
    VIETNAM_INDEPENDENT_DAY,
    LUNAR_NEW_YEAR,
    COMMON_WORKDAYS_IN_WEEK,
    COMMON_DAILY_SHIFTS,
)

YEAR = MONTH = DAY = int
SPECIFIED_SHIFTS = Dict[date, DailyShift]
WEEKDAY = Annotated[int, AfterValidator(check_valid_weekday)]
WEEKDAYS = Set[WEEKDAY]


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
    days_off: List[DateRange] = [
        VIETNAM_VICTORY_DAY,
        VIETNAM_INDEPENDENT_DAY,
        THE_HUNG_KINGS_TEMPLE_FESTIVAL,
        LUNAR_NEW_YEAR,
        SOLAR_NEW_YEAR,
        INTERNATIONAL_LABOR_DAY,
    ]
    special_shifts: SPECIFIED_SHIFTS = {}

    def partial_copy(
        self,
        workdays_weekly: List[int] | None = None,
        shifts_daily: DailyShift | None = None,
        days_off: List[DateRange] | None = None,
        special_shifts: SPECIFIED_SHIFTS | None = None,
    ) -> "ShiftsBuilder":
        return ShiftsBuilder(
            workdays_weekly=workdays_weekly
            if workdays_weekly
            else self.workdays_weekly,
            shifts_daily=shifts_daily if shifts_daily else self.shifts_daily,
            days_off=days_off if days_off else self.days_off,
            special_shifts=special_shifts if special_shifts else self.special_shifts,
        )

    def add_days_off(
        self, days_off: DateRange, inplace: bool = False
    ) -> Optional["ShiftsBuilder"]:
        if inplace:
            self.days_off.append(days_off)
            return
        return self.partial_copy(days_off=self.days_off + [days_off])

    def add_workday_weekly(
        self, workday: WEEKDAY, inplace: bool = False
    ) -> Optional["ShiftsBuilder"]:
        if inplace:
            self.workdays_weekly.add(workday)
            return
        return self.partial_copy(workdays_weekly=self.workdays_weekly.union({workday}))

    def update_workdays_weekly(
        self, workdays: WEEKDAYS, inplace: bool = False
    ) -> Optional["ShiftsBuilder"]:
        if inplace:
            self.workdays_weekly = workdays
            return
        return self.partial_copy(workdays_weekly=workdays)

    def update_days_off(
        self, days_off: List[DateRange], inplace: bool = False
    ) -> Optional["ShiftsBuilder"]:
        if inplace:
            self.days_off = days_off
            return
        return self.partial_copy(days_off=days_off)

    def update_special_shifts(
        self, custom_shifts: SPECIFIED_SHIFTS, inplace: bool = False
    ) -> Optional["ShiftsBuilder"]:
        if inplace:
            self.special_shifts.update(custom_shifts)
            return
        new_shifts = self.special_shifts.copy()
        new_shifts.update(custom_shifts)
        return self.partial_copy(special_shifts=new_shifts)

    def generate_shifts(self) -> DailyShift:
        pass
