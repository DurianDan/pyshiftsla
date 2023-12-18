from datetime import date, time, datetime
from typing import Dict, Set, Literal, List
from pydantic import RootModel

from pysla.daily_shifts import DailyShift
from pysla.datetime_utilities import Milliseconds, diff_datetime


class ShiftRange(RootModel):
    root: Dict[date, DailyShift]

    def __getitem__(self, key: date) -> DailyShift | None:
        if not isinstance(key, date):
            raise NotImplementedError(
                f"Only accept key as `date` not {type(key)}"
            )
        return self.root[key]

    def __setitem__(self, key: date, value: DailyShift | None):
        self.root.update({key: value})

    def update(self, to_update: "ShiftRange") -> None:
        self.root.update(to_update.root)

    def total_milliseconds(self, exclude: List[date] = []) -> Milliseconds:
        return sum(
            [
                daily_shifts.total_milliseconds()
                for specified_date, daily_shifts in self.root.items()
                if specified_date not in exclude
            ]
        )

    def work_amount_in_shiftrannge(
        self,
        start_work: datetime,
        end_work: datetime,
        default_if_no_shifts_are_between: Literal["diff"] | int = "diff",
    ) -> Milliseconds:
        start_work_date, end_work_date = start_work.date(), end_work.date()
        if start_work_date == end_work_date:
            return self.root[start_work_date].work_amount_in_shifts(
                start_work, end_work, default_if_no_shifts_are_between
            )
        else:
            start_day_workamount = self.root[
                start_work_date
            ].work_amount_in_shifts(
                start_work.time(),
                time(23, 59),
                default_if_no_shifts_are_between,
            )
            end_day_workamount = self.root[end_work_date].work_amount_in_shifts(
                time(0, 1), end_work.time(), default_if_no_shifts_are_between
            )
            remaining_shifts = self.total_milliseconds(
                [start_work_date, end_work_date]
            )
            calculated_workamount = (
                start_day_workamount + end_day_workamount + remaining_shifts
            )
            if calculated_workamount == 0:
                return (
                    diff_datetime(start_work, end_work)
                    if default_if_no_shifts_are_between == "diff"
                    else default_if_no_shifts_are_between
                )
