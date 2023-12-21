from typing import List, Literal, Optional
import polars as pl
from pydantic import BaseModel
from datetime import date, datetime
from lunardate import LunarDate

CALENDAR_TYPE = Literal["lunar", "solar"]


class DateRangeConfig(BaseModel):
    start: date
    end: Optional[date] = None
    calendar_type: CALENDAR_TYPE = "solar"


class DateRange(DateRangeConfig):
    @staticmethod
    def fromstr(
        daterange_str: str,
        calendar_type: CALENDAR_TYPE = "solar",
        date_format: str = "%Y%m%d",
    ) -> "DateRange":
        dates_component = daterange_str.strip().split("-")
        invalid_daterange_str = f"Date range must be in the format '{date_format}-{date_format}' or '{date_format}', invalid: {daterange_str}"
        assert len(dates_component) in [1, 2], invalid_daterange_str
        end_date = None
        try:
            format_datestr = lambda idx: datetime.strptime(  # noqa: E731
                dates_component[idx], date_format
            ).date()
            if len(dates_component) == 2 and dates_component[1] != "":
                end_date = format_datestr(1)
            return DateRange(
                start=format_datestr(0),
                end=end_date,
                calendar_type=calendar_type,
            )
        except Exception as err:
            raise ValueError(invalid_daterange_str) from err

    @property
    def solar_daterange(self) -> "DateRange":
        """
        Get solar `DateRange`, whatever the `calendar_type` is.
        """
        match self.calendar_type:
            case "solar":
                return self
            case "lunar":
                return self.lunar_to_solar_daterange()

    @property
    def dates(self) -> List[date]:
        """
        Return a list of dates, inside the date range, including the start and end date.
        """
        daterange = self.solar_daterange
        if not self.end:
            return [daterange.start]
        dates_in_range: List[date] = pl.date_range(
            start=daterange.start, end=daterange.end, eager=True
        ).to_list()
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
