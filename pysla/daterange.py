from typing import List, Literal, Optional, Tuple
import pandas as pd
from pydantic import BaseModel
from datetime import date, datetime
from lunardate import LunarDate

CALENDAR_TYPE = Literal["lunar", "solar"]


class DateRangeConfig(BaseModel):
    start: date
    end: date
    calendar_type: CALENDAR_TYPE = "solar"


class DateRange(DateRangeConfig):
    @staticmethod
    def fromstr(
        daterange_str: str,
        calendar_type: CALENDAR_TYPE = "solar",
        date_format: str = "%Y%m%d",
    ) -> "DateRange":
        dates_component = daterange_str.strip().split("-")
        invalid_daterange_str = f"Date range must be in the format '{date_format}-{date_format}', invalid: {daterange_str}"
        assert len(dates_component) == 2, invalid_daterange_str
        try:
            format_datestr = lambda idx: datetime.strptime(  # noqa: E731
                dates_component[idx], date_format
            ).date()
            return DateRange(
                start=format_datestr(0),
                end=format_datestr(1),
                calendar_type=calendar_type,
            )
        except Exception as err:
            raise ValueError(invalid_daterange_str) from err

    def partial_copy_date(
        self,
        date: date,
        month: int | None = None,
        year: int | None = None,
        day: int | None = None,
    ) -> date:
        new_date = date.replace()
        if year:
            new_date.replace(year=year)
        if month:
            new_date.replace(month=month)
        if day:
            new_date.replace(day=day)
        return new_date

    def update(
        self,
        year: int | None = None,
        month: int | None = None,
        day: int | None = None,
        calendar_type: CALENDAR_TYPE | None = None,
        inplace: bool = False,
    ) -> Optional["DateRange"]:
        new_start = self.partial_copy_date(self.start, year, month, day)
        new_end = self.partial_copy_date(self.end, year, month, day)
        if inplace:
            self.start = new_start
            self.end = new_end
            if calendar_type:
                self.calendar_type = calendar_type
            return None
        else:
            return DateRange(
                start=new_start,
                end=new_end,
                calendar_type=calendar_type
                if calendar_type
                else self.calendar_type,
            )

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
        solar_date_end = LunarDate(
            self.end.year, self.end.month, self.end.day
        ).toSolarDate()
        return DateRange(start=solar_date_start, end=solar_date_end)

    def substract(self, other_range: "DateRange") -> List["DateRange"]:
        pass


if __name__ == "__main__":
    pass
