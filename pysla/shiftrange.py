from datetime import date
from typing import Dict
from pydantic import RootModel

from .daily_shifts import DailyShift


class ShiftRange(RootModel):
    root: Dict[date, DailyShift | None]

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
