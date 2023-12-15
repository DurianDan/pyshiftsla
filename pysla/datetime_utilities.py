from typing import List, Literal
from datetime import time, datetime, timedelta

Milliseconds = int
WEEKDAYS_INDEXES = [0, 1, 2, 3, 4, 5, 6]


def milliseconds_from_day_start(to_convert: time) -> Milliseconds:
    hour_to_milli = to_convert.hour * 60 * 60 * 1000
    minutes_to_milli = to_convert.minute * 60 * 1000
    micro_to_milli = to_convert.microsecond * 1000
    return hour_to_milli + minutes_to_milli + micro_to_milli


def diff_time(start: time, end: time) -> Milliseconds:
    start_period_from_start_day = milliseconds_from_day_start(start)
    end_period_from_start_day = milliseconds_from_day_start(end)
    return end_period_from_start_day - start_period_from_start_day


def diff_datetime(start: datetime, end: datetime) -> Milliseconds:
    diff_obj: timedelta = end - start
    return diff_obj.seconds * 1000


def check_start_end_event(start: datetime | time, end: datetime | time) -> None:
    assert type(start) is type(
        end
    ), f"Mismatched types between start: {start} and end: {end}"
    assert (
        end > start
    ), f"'Start' event must happened before 'End' event, parsed values: start({start}), end({end})"


def check_events_same_day(events: List[datetime]) -> bool:
    first_event_date = events[0].date()
    return all(event.date() == first_event_date for event in events[1:])


def compare_times(
    time_left: time, time_right: time
) -> Literal["geater", "smaller", "equal"]:
    if time_left > time_right:
        return "greater"
    elif time_left == time_right:
        return "equal"
    else:
        return "smaller"


def check_valid_weekday(weekday: int) -> List[int]:
    assert (
        weekday in WEEKDAYS_INDEXES
    ), f"{weekday} is out of weekdays indexes: [0,1,2,3,4,5,6]"
    return weekday
