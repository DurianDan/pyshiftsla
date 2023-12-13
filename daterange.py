from typing import List, Literal, Optional
import pandas as pd
from pydantic import BaseModel
from datetime import date
from lunardate import LunarDate

class DateRange(BaseModel):
    start: date
    end: Optional[date]
    calendar_type: Literal['lunar', 'solar'] = 'solar'

    def get_solar_daterange(self) -> 'DateRange':
        '''
        Get solar `DateRange`, whatever the calendar is.
        '''
        if self.calendar_type == 'solar': return self
        else: return self.lunar_to_solar_daterange()
    
    def to_dates(self) -> List[date]:
        '''
        Return a list of dates, inside the date range, including the start and end date.
        '''
        daterange = self.get_solar_daterange()
        if not self.end: return [daterange.start]
        datetime_in_range = pd.date_range(
            start=daterange.start,
            end=daterange.end,
            freq="d").to_pydatetime().tolist()
        dates_in_range = [dt.date() for dt in datetime_in_range]
        return dates_in_range

    def lunar_to_solar_daterange(self) -> 'DateRange':
        '''
        Turn lunar `DateRange` into solar `DateRange`
        '''
        solar_date_start = LunarDate(
            self.start.year, self.start.month, self.start.day).toSolarDate()
        solar_date_end = None
        if self.end:
            solar_date_end = LunarDate(
                self.end.year, self.end.month, self.end.day).toSolarDate()
        return DateRange(start=solar_date_start, end=solar_date_end)