from pydantic import RootModel
from typing import List
from datetime import datetime
from .datetime_utilities import Milliseconds
from .shift import Shift


class DailyShift(RootModel):
    """
    Shifts in a day, represented by a list of `Shift` objects,
     these `Shift`s are not overlapped and
     have the total milliseconds smaller than or equal to a day
     (1day = 24hours = 24*60*60*1000Milliseconds)
    """

    root: List[Shift]

    def __iter__(self) -> List[Shift]:
        return self.root

    def __getitem__(self, idx: int) -> Shift | None:
        if not isinstance(idx, int):
            raise NotImplementedError(f"Only accept index as `int` not {type(idx)}")
        return self.root[idx]

    def resolve_overlap(self):
        pass

    def total_milliseconds(self) -> Milliseconds:
        return sum([shift.diff for shift in self])

    def work_amount_in_shifts(
        self, start_work: datetime, end_work: datetime
    ) -> Milliseconds:
        pass
