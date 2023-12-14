from datetime import date, time
from .daterange import DateRange
from .shifts import Shift, DailyShift

VIETNAM_VICTORY_DAY = DateRange(start=date(2024, 4, 30))
SOLAR_NEW_YEAR = DateRange(start=date(2024, 1, 1))
INTERNATIONAL_LABOR_DAY = DateRange(start=date(2024, 5, 1))
THE_HUNG_KINGS_TEMPLE_FESTIVAL = DateRange(
    start=date(2024, 3, 10),
    calendar_type="lunar")
VIETNAM_INDEPENDENT_DAY = DateRange(
    start=date(2024, 9, 2),
    end=date(2024, 9, 3),
    )
LUNAR_NEW_YEAR = DateRange(
    start=date(2024,1,1),
    end=date(2024,1,5),
    calendar_type='lunar'
    )
COMMON_WEEKDAYS = [0,1,2,3,4]
COMMON_DAILY_SHIFTS = DailyShift([
        Shift(start=time(8,30), end=time(11,45)),
        Shift(start=time(13,15), end=time(17,45)),
    ])