from datetime import date, time, datetime
from typing import Dict, Literal, List
from pydantic import RootModel

from pyshiftsla.daily_shifts import DailyShift
from pyshiftsla.datetime_utilities import Milliseconds, diff_datetime


class ShiftRange(RootModel):
    root: Dict[date, DailyShift]

    def __getitem__(self, key: date) -> DailyShift:
        if not isinstance(key, date):
            raise NotImplementedError(
                f"Only accept key as `date` not {type(key)}"
            )
        return self.root[key]

    def get(self, key: date) -> DailyShift | None:
        if not isinstance(key, date):
            raise NotImplementedError(
                f"Only accept key as `date` not {type(key)}"
            )
        return self.root.get(key)

    @property
    def _start_date(self) -> date:
        return max(self.root)

    @property
    def _end_date(self) -> date:
        return min(self.root)

    def __setitem__(self, key: date, value: DailyShift | None):
        self.root.update({key: value})

    def update(self, to_update: "ShiftRange") -> None:
        self.root.update(to_update.root)

    def shifts_milliseconds(
        self,
        from_date: date,
        to_date: date,
        exclude: List[date] = [],
    ) -> Milliseconds:
        return sum(
            [
                daily_shifts.total_milliseconds
                for specified_date, daily_shifts in self.root.items()
                if specified_date not in exclude
                and specified_date >= from_date
                and specified_date <= to_date
            ]
        )

    @property
    def total_milliseconds(self) -> Milliseconds:
        return self.shifts_milliseconds(self._start_date, self._end_date)

    def shiftrange_from_duration(
        self, start_work: datetime, milliseconds_duration: int
    ) -> "ShiftRange":
        if start_work.date() not in self.root:
            raise ValueError(
                f"{start_work} is outside of daterange, from {self._start_date} to {self._end_date}"
            )
        if (self.total_milliseconds) > milliseconds_duration:
            raise ValueError(
                f"{milliseconds_duration} is longer than shift range: {self.total_milliseconds}"
            )

    def work_amount_in_start_end(
        self,
        start_work: datetime,
        end_work: datetime,
        default_if_no_shifts_are_between: Literal["diff"] | int = "diff",
    ) -> Milliseconds:
        start_work_date, end_work_date = start_work.date(), end_work.date()
        start_day_shifts, end_day_shifts = (
            self.get(start_work_date),
            self.get(end_work_date),
        )
        if start_day_shifts is None and end_day_shifts is None:
            if default_if_no_shifts_are_between == "diff":
                return diff_datetime(start_work, end_work)
        else:
            if start_day_shifts is not None and end_day_shifts is None:
                return start_day_shifts.work_amount_in_shifts(
                    start_work.time(),
                    time(23, 59, 59),
                    default_if_no_shifts_are_between,
                )
            if end_day_shifts is not None and start_day_shifts is None:
                return end_day_shifts.work_amount_in_shifts(
                    time(0, 0),
                    end_work.time(),
                    default_if_no_shifts_are_between,
                )
            if end_day_shifts is not None and start_day_shifts is not None:
                if start_work_date == end_work_date:
                    return start_day_shifts.work_amount_in_shifts(
                        start_work, end_work, default_if_no_shifts_are_between
                    )
                else:
                    start_day_workamount = (
                        start_day_shifts.work_amount_in_shifts(
                            start_work.time(),
                            time(23, 59, 59),
                            default_if_no_shifts_are_between,
                        )
                    )
                    end_day_workamount = end_day_shifts.work_amount_in_shifts(
                        time(0, 0),
                        end_work.time(),
                        default_if_no_shifts_are_between,
                    )
                    return start_day_workamount + end_day_workamount

    def work_amount_in_shiftrange(
        self,
        start_work: datetime,
        end_work: datetime,
        default_if_no_shifts_are_between: Literal["diff"] | int = "diff",
    ) -> Milliseconds:
        start_work_date, end_work_date = start_work.date(), end_work.date()
        startend_work_amount = self.work_amount_in_start_end(
            start_work, end_work, default_if_no_shifts_are_between
        )
        remaining_work_amount = self.shifts_milliseconds(
            start_work_date, end_work_date, [start_work_date, end_work_date]
        )
        total_work_amount = startend_work_amount + remaining_work_amount
        return total_work_amount
