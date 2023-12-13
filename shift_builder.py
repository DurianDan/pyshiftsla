from typing import Dict, List
from pydantic import BaseModel
from datetime import date, time
from daterange import DateRange
from shifts import Shift, Shifts
from common_daysoff import (
    VIETNAM_VICTORY_DAY,
    SOLAR_NEW_YEAR,
    INTERNATIONAL_LABOR_DAY,
    THE_HUNG_KINGS_TEMPLE_FESTIVAL,
    VIETNAM_INDEPENDENT_DAY,
    LUNAR_NEW_YEAR,
    COMMON_WEEKDAYS,
    COMMON_DAILY_SHIFTS
)

class ShiftsBuilder(BaseModel):
    '''
    `Shifts` configuration for a single `employee/team/firm`. use method `generate_shifts` for generating Shifts based on parsed config.

    To generate shifts, the order of priorities is `special_shifts` > `days_off` > `shifts_daily` + `workdays_weekly`

    :param workdays_weekly: indexes of work days in a week, default is from Monday to Friday [0,1,2,3,4]
    :param shifts_daily: default `Shifts` in a typical workday.
    :param days_off: List of days off, can be *lunar* or *solar* days off
    :param special_shifts: special `Shifts` of a *specific date*, if `None`, that day will have zero shifts.
    '''
    workdays_weekly: List[int] = COMMON_WEEKDAYS
    shifts_daily: Shifts = COMMON_DAILY_SHIFTS
    days_off: List[DateRange] = [
        VIETNAM_VICTORY_DAY,
        VIETNAM_INDEPENDENT_DAY,
        THE_HUNG_KINGS_TEMPLE_FESTIVAL,
        LUNAR_NEW_YEAR,

        SOLAR_NEW_YEAR,
        INTERNATIONAL_LABOR_DAY,
    ]
    special_shifts: Dict[date, None|Shifts] = {
        date(2023, 18, 4): Shifts(shifts=[Shift(start=time(19,45), end=time(23,30))])
    }

    def generate_shifts(self) -> Shifts:
        pass