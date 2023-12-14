from typing import List, Optional, Literal, Tuple
from pydantic import BaseModel, RootModel, model_validator
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

def compare_times(
    time_left: time,
    time_right: time
) -> Literal['geater', 'smaller', "equal"]:
    if time_left>time_right: return 'greater'
    elif time_left == time_right: return 'equal'
    else: return 'smaller'

COMPARE_TO_ANOTHER_SHIFT = Literal[ # comparing -___- to |___|
    'smaller', # -___-  |___|
    'greater', # |___|  -___-
    'equal', # +___+
    'following', # -_|__-_|
    'leading', # |_-__|_-
    'same-end-following', # -__|__+ 
    'same-start-leading', # +__|__-
    'contain' # -__|__|__-
    'be-contained' # |__-__-__|
    'end-connects-start', # -___+___|
    'start-connects-end', # |___+___-
    ]

class Shift(BaseModel):
    start: time
    end: time

    @model_validator(mode='after')
    def start_must_happend_before_end(self) -> 'Shift':
        check_start_end_event(self.start, self.end)
        return self

    @property
    def diff(self) -> Milliseconds:
        return diff_time(self.start, self.end)

    def is_in_shift(self, event: time) -> bool:
        return (
            event > self.start and
            event < self.end)
    
    def work_amount_in_shift(
        self,
        start_work: time,
        end_work: time
    ) -> Milliseconds:
        '''
        Calculate how much a work takes up a shift. return the milliseconds(int) that work takes

        :param start_work: Starts Work Event
        :param end_work: Ends Work Event
        :rtype: Milliseconds
        '''
        check_start_end_event(start_work, end_work)
        match self.is_in_shift(start_work), self.is_in_shift(end_work):
            case True, True: return diff_time(start_work, end_work)
            case True, False: return diff_time(start_work, self.end)
            case False, True: return diff_time(self.start, end_work)
            case False, False: 
                if start_work < self.start and end_work > self.end:
                    return self.diff
                else:
                    raise diff_time(start_work, end_work)

    def resolve(
        self,
        other: 'Shift',
        strategy: Literal['inner', 'outer'] = 'inner'
    )-> List['Shift']:
        '''Resolve another overlapped `Shift`s, if not overlapped return themself.
        
        :param other: the other `Shift` to resolve
        :param strategy: 'inner' is for getting the overlapped `Shift` inside both of them.
        'outer' is for getting the `Shift`s that are not overlapped. default is 'inner'
        '''
        overlapped_shift = self & other
        if strategy=="inner": return overlapped_shift
    
    def compare(
        self, 
        other: 'Shift'
    ) -> COMPARE_TO_ANOTHER_SHIFT:
        if self > other: return 'greater'
        elif self < other: return 'smaller'
        match (
            compare_times(self.start,other.end),
            compare_times(self.end,other.start)
        ):
            case 'equal', _: return 'start-connects-end'
            case _, 'equal': return 'end-connects-start'
            case 'greater', _: return 'greater'
            case _, "smaller": return 'smaller'

        match (
            compare_times(self.start,other.start),
            compare_times(self.end,other.end)
        ):
            case 'equal', 'equal': return 'equal'
            
            case 'smaller', 'smaller': return 'following'
            case 'greater', 'greater': return 'leading'

            case 'equal', 'smaller': return 'contain'
            case 'greater', 'equal': return 'contain'
            case 'smaller', 'greater': return 'contain'

            case 'greater', 'smaller': return 'be-contained'

            case 'smaller', 'equal': return 'same-end-following'
            case 'equal', 'greater': return 'same-start-leading'

    def get_overlap(self, other: 'Shift') -> Optional['Shift']:
        '''Check if 2 shifts are overlap, and overlap how much with each other.
        return another `Shift` if overlapped, and `None` if not overlap 
        '''
        start_overlap = self.start
        end_overlap = self.end
        compared  = self.compare(other)
        match compared:
            case 'smaller' | 'greater': return None
            case 'following': start_overlap = other.start
            case 'leading': end_overlap = other.end
            case 'contain': return other
            case 'equal': return self
        return Shift(
            start=start_overlap,
            end=end_overlap)

    def __ne__(self, other: 'Shift') -> bool:
        '''different than. No overlap at all'''
        return self > other or self < other

    def __gt__(self, other: 'Shift') -> bool:
        '''greater than'''
        return self.start > other.end

    def __lt__(self, other: 'Shift') -> bool:
        '''less than'''
        return self.end < other.start

    def __eq__(self, other: 'Shift') -> bool:
        '''equal to'''
        return (
            self.start == other.start and
            self.end == other.end)

def sorted_shifts(
    shifts: List[Shift]) -> List[Shift]:
    pass

class DailyShift(RootModel):
    '''
    Shifts in a day, represented by a list of `Shift` object,
     these `Shift`s are not overlapped and
     have the total milliseconds smaller than or equal to a day
     (1day = 24hours = 24*60*60*1000Milliseconds)
    '''
    root: List[Shift]

    def __iter__(self) -> List[Shift]:
        return iter(self.root)

    def __getitem__(self, idx: int) -> Shift|None:
        if not isinstance(idx, int):
            raise NotImplementedError(f"Only accept index as `int` not {type(idx)}")
        return self.root[idx]

    def resolve_overlap(self)
    def total_milliseconds(self) -> Milliseconds:
        return sum([shift.diff for shift in self])

    def work_amount_in_shifts(
        self,
        start_work: datetime,
        end_work: datetime
    ) -> Milliseconds:
        pass
