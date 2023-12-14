from typing import List
from pydantic import BaseModel, model_validator
from datetime import time, datetime, timedelta

Milliseconds = int
def milliseconds_from_day_start(to_convert: time) -> Milliseconds:
    hour_to_milli = to_convert.hour*60*60*1000
    minutes_to_milli = to_convert.minute*60*1000
    micro_to_milli = to_convert.microsecond*1000
    return hour_to_milli + minutes_to_milli + micro_to_milli

def diff_time(start: time, end: time) -> Milliseconds:
    start_period_from_start_day = milliseconds_from_day_start(start)
    end_period_from_start_day = milliseconds_from_day_start(end)
    return end_period_from_start_day - start_period_from_start_day

def diff_datetime(start: datetime, end: datetime) -> Milliseconds:
    diff_obj: timedelta = (end - start)
    return diff_obj.seconds * 1000

def check_start_end_event(start: datetime|time, end: datetime|time) -> None:
    assert type(start) is type(end), f"Mismatched types between start: {start} and end: {end}"
    assert end > start, f"'Start' event must happened before 'End' event, parsed values: start({start}), end({end})"

def check_events_same_day(events: List[datetime]) -> bool:
    first_event_date = events[0].date()
    return all([
        event.date() == first_event_date
        for event in  events[1:]
    ])

class Shift(BaseModel):
    start: datetime|time
    end: datetime|time

    @model_validator(mode='after')
    def must_be_in_a_day(self) -> 'Shift':
        check_start_end_event(self.start, self.end)
        match isinstance(self.start, time), isinstance(self.end, time):
            case False, False:
                assert check_events_same_day([self.start, self.end]), "'Start' and 'End' of a shift must be in a day"
        return self

    @property
    def diff(self) -> Milliseconds:
        if isinstance(self.start, time): return diff_time(self.start, self.end)
        return diff_datetime(self.start, self.end)
    
    def check_event_same_type_as_shift(self, event: time|datetime) -> time|datetime:
        assert type(event) is not type(self.start), f"Event's type mismatch Shift type: {type(self.start)}"
        return event

    def is_in_shift(self, event: time|datetime) -> bool:
        self.check_event_same_type_as_shift(event)
        return all([
            event > self.start,
            event < self.end,
        ])
    
    def work_amount_in_shift(
        self,
        start_work: datetime,
        end_work: datetime
    ) -> Milliseconds:
        '''
        Calculate how much a work takes up a shift. return the milliseconds(int) that work takes

        :param start_work: Starts Work Event
        :param end_work: Ends Work Event
        :rtype: Milliseconds
        '''
        check_start_end_event(start_work, end_work)
        match self.is_in_shift(start_work), self.is_in_shift(end_work):
            case True, True: return diff_datetime(start_work, end_work)
            case True, False: return diff_datetime(start_work, self.end)
            case False, True: return diff_datetime(self.start, end_work)
            case False, False: 
                if start_work < self.start and end_work > self.end:
                    return self.diff
                else:
                    raise diff_datetime(start_work, end_work)

class Shifts(BaseModel):
    shifts: List[Shift]

    def total_milliseconds(self) -> Milliseconds:
        return sum([shift.diff for shift in self.shifts])

    def work_amount_in_shifts(
        self,
        start_work: datetime,
        end_work: datetime
    ) -> Milliseconds:
        pass
