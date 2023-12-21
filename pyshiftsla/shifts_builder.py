from typing import List, Optional, Set, Literal
from pydantic import BaseModel
from datetime import date, datetime
import numpy as np
import numpy.typing as npt
import polars as pl

from pyshiftsla.shiftrange import ShiftRange
from pyshiftsla.daterange import DateRange
from pyshiftsla.daily_shifts import DailyShift
from pyshiftsla.datetime_utilities import Milliseconds
from pyshiftsla.common_daysoff import (
    COMMON_WORKDAYS_IN_WEEK,
    COMMON_DAILY_SHIFTS,
    WEEKDAYS,
)

YEAR = MONTH = DAY = int


class ShiftsBuilder(BaseModel):
    """
    `Shifts` configuration for a single `employee/team/firm`. Use method `build_shifts_from_daterange` for generating `Shift`s based on parsed config. Use method `calculate_sla` for calculating sla based on generated `Shift`s

    To generate shifts, the order of priorities is `special_shifts` > `days_off` > `shifts_daily` + `workdays_weekly`

    :param workdays_weekly: indexes of work days in a week, default is from Monday to Friday [0,1,2,3,4]
    :param shifts_daily: default `Shifts` in a typical workday.
    :param days_off: List of days off, can be *lunar* or *solar* days off
    :param special_shifts: special `Shifts` of a *specific date*
    """

    workdays_weekly: WEEKDAYS = COMMON_WORKDAYS_IN_WEEK
    shifts_daily: DailyShift = COMMON_DAILY_SHIFTS
    days_off_ranges: List[DateRange | date] = []
    special_shifts: ShiftRange = ShiftRange({})

    _generated_shifts: ShiftRange | None = None

    @property
    def _days_off(self) -> Set[date]:
        if len(self.days_off_ranges) == 0:
            return set()
        days_off = set()
        for dates_indicator in self.days_off_ranges:
            if isinstance(dates_indicator, date):
                days_off.add(dates_indicator)
            else:
                days_off.update(dates_indicator.dates)
        return days_off

    @property
    def _numpy_busday_weekmask(self) -> List[Literal[1, 0]]:
        weekmask = 7 * [0]
        for day_idx in self.workdays_weekly:
            weekmask[day_idx] = 1
        return weekmask

    def is_workday(
        self,
        dates_to_check: List[date],
        returned_as: Literal["filtered_dates", "checks_array"] = "checks_array",
    ) -> npt.NDArray[np.bool_]:
        checks = np.is_busday(
            dates_to_check,
            weekmask=self._numpy_busday_weekmask,
            holidays=list(self._days_off),
        )
        if returned_as == "filtered_dates":
            return np.array(dates_to_check)[checks]
        return checks

    def get_workdays(self, from_date: date, to_date: date) -> List[date]:
        raw_dates = pl.date_range(
            start=from_date, end=to_date, eager=True
        ).to_list()
        return self.is_workday(raw_dates, returned_as="filtered_dates").tolist()

    def get_days_off(self) -> Set[date]:
        return self._days_off

    def partial_config_copy(
        self,
        workdays_weekly: WEEKDAYS | None = None,
        shifts_daily: DailyShift | None = None,
        days_off_ranges: List[DateRange | date] | None = None,
        special_shifts: ShiftRange | None = None,
    ) -> "ShiftsBuilder":
        return ShiftsBuilder(
            shifts_daily=shifts_daily if shifts_daily else self.shifts_daily,
            days_off_ranges=days_off_ranges
            if days_off_ranges
            else self.days_off_ranges,
            workdays_weekly=workdays_weekly
            if workdays_weekly
            else self.workdays_weekly,
            special_shifts=special_shifts
            if special_shifts
            else self.special_shifts,
        )

    def add_days_off_range(
        self, days_off_range: DateRange | date, inplace: bool = False
    ) -> Optional["ShiftsBuilder"]:
        if inplace:
            self.days_off_ranges.append(days_off_range)
            return
        return self.partial_config_copy(
            days_off_ranges=self.days_off_ranges + [days_off_range]
        )

    def update_workday_weekly(
        self, workdays: WEEKDAYS, inplace: bool = False
    ) -> Optional["ShiftsBuilder"]:
        if inplace:
            self.workdays_weekly.update(workdays)
            return
        return self.partial_config_copy(
            workdays_weekly=self.workdays_weekly.union(workdays)
        )

    def update_special_shifts(
        self,
        special_shifts: ShiftRange,
        inplace: bool = False,
    ) -> Optional["ShiftsBuilder"]:
        if inplace:
            self.special_shifts.update(special_shifts)
        return self.partial_config_copy(special_shifts=special_shifts)

    def calculate_work_days_between(
        self,
        start_deal: date,
        end_deal: date,
    ) -> int:
        return np.busday_count(
            start_deal,
            end_deal,
            self._numpy_busday_weekmask,
            self._days_off,
        )

    def build_shifts_from_daterange(
        self, from_date: datetime, to_date: datetime
    ) -> ShiftRange:
        """
        Build `Shift`s from `from_date` and `to_date`
        :param `from_date`: start date of the range
        :param `to_date`: end date of the range
        :return: `ShiftRange` with `Shift`s
        """
        workdays = self.get_workdays(from_date, to_date)
        self._generated_shifts = ShiftRange(
            {workday: self.shifts_daily for workday in workdays}
        )
        self._generated_shifts.update(self.special_shifts)
        return self._generated_shifts

    def get_generated_shifts(self) -> ShiftRange | None:
        return self._generated_shifts

    def calculate_sla(
        self,
        start_deal: datetime,
        end_deal: datetime,
        use_generated_shifts: bool = False,
        default_if_no_shifts_are_between: Literal["diff"] | int = "diff",
    ) -> Milliseconds:
        """
        Calculate sla based on `start_deal` and `end_deal`
        :param `use_generated_shifts`: If `False`, `ShiftRange`s will be generated from `start_deal` and `end_deal`. If `True`, `ShiftRange` will be reused, generated from other methods (`build_shifts_from_daterange`)
        :param `default_if_no_shifts_are_between`: is used no `Shift`s are found between `start_deal` and `end_deal`. If `"diff"`, method will calculate `Milliseconds` between `start_deal` and `end_deal`
        """
        start_deal_date, end_deal_date = start_deal.date(), end_deal.date()
        if use_generated_shifts:
            self.build_shifts_from_daterange(start_deal_date, end_deal_date)
        return self._generated_shifts.work_amount_in_shiftrange(
            start_deal, end_deal, default_if_no_shifts_are_between
        )

    def build_shifts_from_duration(
        self,
        hours_duration: int,
        from_timestamp: datetime = datetime.now(),
        use_generated_shifts: bool = False,
    ) -> ShiftRange:
        """
        Build `Shift`s from `hours` based on `from_timestamp`
        """
        pass
