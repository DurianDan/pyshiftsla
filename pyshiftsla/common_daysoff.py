from datetime import date, time
from .daterange import DateRange
from .daily_shifts import Shift, DailyShift
from .datetime_utilities import check_valid_weekday
from pydantic import AfterValidator
from typing_extensions import Annotated
from typing import Set


WEEKDAY = Annotated[int, AfterValidator(check_valid_weekday)]
WEEKDAYS = Set[WEEKDAY]

COMMON_WORKDAYS_IN_WEEK: WEEKDAYS = {0, 1, 2, 3, 4}
COMMON_DAILY_SHIFTS = DailyShift(
    [
        Shift(start=time(8, 30), end=time(11, 45)),
        Shift(start=time(13, 30), end=time(18, 00)),
    ]
)
