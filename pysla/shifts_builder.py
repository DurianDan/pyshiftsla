from typing import List, Optional, Set, Literal, Dict
from pydantic import BaseModel
from datetime import date, datetime
import numpy as np
import numpy.typing as npt
import pandas as pd

from pysla.shiftrange import ShiftRange
from pysla.daterange import DateRange
from pysla.daily_shifts import DailyShift
from pysla.shift import Shift
from pysla.datetime_utilities import Milliseconds
from pysla.common_daysoff import (
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
    :param special_shifts: special `Shifts` of a *specific date*
    """

    workdays_weekly: WEEKDAYS = COMMON_WORKDAYS_IN_WEEK
    shifts_daily: DailyShift = COMMON_DAILY_SHIFTS
    days_off_ranges: List[DateRange] = []
    special_shifts: ShiftRange = ShiftRange({})

    generated_shifts: ShiftRange | None = None

    @property
    def _days_off(self) -> Set[date]:
        return {
            day_off
            for days_off_range in self.days_off_ranges
            for day_off in days_off_range.dates  # generated dates of each `DateRange`
            # 'dates' specified in `special_shifts` overwrite dates in `days_off_ranges`
            if day_off not in self.special_shifts
        }

    @property
    def _numpy_busday_weekmask(self) -> List[Literal[1, 0]]:
        weekmask = 7 * [0]
        for day_idx in self.workdays_weekly:
            weekmask[day_idx] = 1
        return weekmask

    def is_workday(self, dates_to_check: List[date]) -> npt.NDArray[bool]:
        return np.is_busday(
            dates_to_check,
            weekmask=self._numpy_busday_weekmask,
            holidays=self._days_off,
        )

    def get_workdays(self, from_date: date, to_date: date) -> List[date]:
        workdays: pd.DatetimeIndex = pd.date_range(
            start=from_date, end=to_date, freq="d"
        )
        return workdays[self.is_workday(workdays)].to_pydatetime().tolist()

    def get_days_off(self) -> Set[date]:
        return self._days_off

    def partial_copy(
        self,
        workdays_weekly: WEEKDAYS | None = None,
        shifts_daily: DailyShift | None = None,
        days_off: List[DateRange] | None = None,
        special_shifts: ShiftRange | None = None,
    ) -> "ShiftsBuilder":
        return ShiftsBuilder(
            generated_shifts=self.generated_shifts,
            shifts_daily=shifts_daily if shifts_daily else self.shifts_daily,
            days_off_ranges=days_off if days_off else self.days_off_ranges,
            workdays_weekly=workdays_weekly
            if workdays_weekly
            else self.workdays_weekly,
            special_shifts=special_shifts
            if special_shifts
            else self.special_shifts,
        )

    def add_days_off_range(
        self, days_off_range: DateRange, inplace: bool = False
    ) -> Optional["ShiftsBuilder"]:
        if inplace:
            self.days_off_ranges.append(days_off_range)
            return
        return self.partial_copy(
            days_off=self.days_off_ranges + [days_off_range]
        )

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
        workdays = self.get_workdays(from_date, to_date)
        self.generated_shifts = ShiftRange(
            {workday: self.shifts_daily for workday in workdays}
        )
        self.generated_shifts.update(self.special_shifts)
        return self.generated_shifts

    def get_generated_shifts(self) -> ShiftRange | None:
        return self.generated_shifts

    def calculate_sla(
        self,
        start_deal: datetime,
        end_deal: datetime,
        use_generated_shifts: bool = False,
        default_if_no_shifts_are_between: Literal["diff"] | int = "diff",
    ) -> Milliseconds:
        start_deal_date, end_deal_date = start_deal.date(), end_deal.date()
        if use_generated_shifts:
            self.build_shifts_from_daterange(start_deal_date, end_deal_date)
        return self.generated_shifts.work_amount_in_shiftrannge(
            start_deal, end_deal, default_if_no_shifts_are_between
        )

    def build_shifts_from_hours(
        self,
        hours: int,
        from_timestamp: datetime = datetime.now(),
    ) -> ShiftRange:
        pass
