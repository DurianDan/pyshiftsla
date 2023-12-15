from typing import Dict, List, Literal, Optional, Iterable
import pandas as pd
from pydantic import BaseModel
from datetime import date
from lunardate import LunarDate


class DateRangeConfig(BaseModel):
    start: date
    end: Optional[date] = None
    calendar_type: Literal["lunar", "solar"] = "solar"


class DateRange(DateRangeConfig):
    @property
    def solar_daterange(self) -> "DateRange":
        """
        Get solar `DateRange`, whatever the `calendar_type` is.
        """
        if self.calendar_type == "solar":
            return self
        else:
            return self.lunar_to_solar_daterange()

    @property
    def dates(self) -> List[date]:
        """
        Return a list of dates, inside the date range, including the start and end date.
        """
        daterange = self.solar_daterange()
        if not self.end:
            return [daterange.start]
        datetime_in_range = (
            pd.date_range(start=daterange.start, end=daterange.end, freq="d")
            .to_pydatetime()
            .tolist()
        )
        dates_in_range: List[date] = [dt.date() for dt in datetime_in_range]
        return dates_in_range

    def lunar_to_solar_daterange(self) -> "DateRange":
        """
        Turn lunar `DateRange` into solar `DateRange`
        """
        solar_date_start = LunarDate(
            self.start.year, self.start.month, self.start.day
        ).toSolarDate()
        solar_date_end = None
        if self.end:
            solar_date_end = LunarDate(
                self.end.year, self.end.month, self.end.day
            ).toSolarDate()
        return DateRange(start=solar_date_start, end=solar_date_end)

    # def from_dates(
    #     self, dates: List[date], sorted_ascending: bool = True
    # ) -> List["DateRange"]:
    #     sorted_dates = sorted()

    def substract(self, other_range: "DateRange") -> List["DateRange"]:
        pass


if __name__ == "__main__":
    pass
