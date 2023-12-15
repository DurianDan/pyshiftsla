from typing import List, Optional, Literal, Union, Tuple, TypedDict
from pydantic import BaseModel, model_validator
from datetime import time
from .datetime_utilities import (
    diff_time,
    check_start_end_event,
    compare_times,
    Milliseconds,
)

COMPARE_TO_ANOTHER_SHIFT_MISMATCH_STARTEND = Literal[  # comparing -___- to |___|
    "smaller",  # -___-  |___|
    "greater",  # |___|  -___-
    "end-connects-start",  # -___+___|
    "start-connects-end",  # |___+___-
]
COMPARE_TO_ANOTHER_SHIFT_MATCH_STARTEND = Literal[  # comparing -___- to |___|
    "equal",  # +___+
    "following",  # -_|__-_|
    "leading",  # |_-__|_-
    "contain",  # -__|__|__-
    "be-contained",  # |__-__-__|
]
COMPARE_TO_ANOTHER_SHIFT = Union[
    COMPARE_TO_ANOTHER_SHIFT_MISMATCH_STARTEND, COMPARE_TO_ANOTHER_SHIFT_MATCH_STARTEND
]
RESOLVE_TWO_SHIFTS_STRATEGY = Literal["inner", "outer", "both"]


class RESOLVED_TWO_SHIFTS(TypedDict):
    inner: Optional["Shift"]
    outer: Optional[List["Shift"]]
    compare_result: COMPARE_TO_ANOTHER_SHIFT


class Shift(BaseModel):
    start: time
    end: time

    @model_validator(mode="after")
    def start_must_happend_before_end(self) -> "Shift":
        check_start_end_event(self.start, self.end)
        return self

    @property
    def diff(self) -> Milliseconds:
        return diff_time(self.start, self.end)

    def is_in_shift(self, event: time) -> bool:
        return event >= self.start and event <= self.end

    def work_amount_in_shift(self, start_work: time, end_work: time) -> Milliseconds:
        """
        Calculate how much a work takes up a shift. return the milliseconds(int) that work takes

        :param start_work: Starts Work Event
        :param end_work: Ends Work Event
        :rtype: Milliseconds
        """
        check_start_end_event(start_work, end_work)
        match self.is_in_shift(start_work), self.is_in_shift(end_work):
            case True, True:
                return diff_time(start_work, end_work)
            case True, False:
                return diff_time(start_work, self.end)
            case False, True:
                return diff_time(self.start, end_work)
            case False, False:
                return self.diff

    def resolve(
        self, other: "Shift", strategy: RESOLVE_TWO_SHIFTS_STRATEGY = "inner"
    ) -> RESOLVED_TWO_SHIFTS:
        """Resolve another overlapped `Shift`s, getting their inner/outer joined Shifts, and the compare result.
            return a `RESOLVED_TWO_SHIFTS`

        :param other: the other `Shift` to resolve
        :param strategy: 'inner' is for getting the overlapped `Shift` inside both of them.
        'outer' is for getting the `Shift`s that are not overlapped. default is 'inner'
        """
        overlapped_shift = self & other
        if strategy == "inner":
            return overlapped_shift

    def _compare_mismatch_startend(
        self, other: "Shift"
    ) -> COMPARE_TO_ANOTHER_SHIFT_MISMATCH_STARTEND | None:
        if self > other:
            return "greater"
        elif self < other:
            return "smaller"
        elif self.start == other.end:
            return "start-connects-end"
        elif self.end == other.start:
            return "end-connects-start"

    def _compare_match_startend(
        self, other: "Shift"
    ) -> COMPARE_TO_ANOTHER_SHIFT_MATCH_STARTEND:
        match (
            compare_times(self.start, other.start),
            compare_times(self.end, other.end),
        ):
            case "equal", "equal":
                return "equal"
            case "smaller", "smaller":
                return "following"
            case "greater", "greater":
                return "leading"

            case "equal", "greater":
                return "contain"
            case "smaller", "equal" | "greater":
                return "contain"

            case "equal", "smaller":
                return "be-contained"
            case "greater", "smaller" | "equal":
                return "be-contained"

    def compare(self, other: "Shift") -> COMPARE_TO_ANOTHER_SHIFT:
        compare_mismatch_startend = self._compare_mismatch_startend(other)
        if compare_mismatch_startend:
            return compare_mismatch_startend
        return self._compare_match_startend(other)

    def resolve(
        self, other: "Shift", strategy: Literal["inner", "outer", "both"]
    ) -> Tuple[COMPARE_TO_ANOTHER_SHIFT, Optional["Shift"]]:
        """Check if 2 shifts are overlap, and overlap how much with each other.
        return another `Shift` if overlapped, and `None` if not overlap
        """
        overlap_shift = Shift(start=self.start, end=self.end)
        compare_result = self.compare(other)
        match compare_result:
            case "smaller" | "greater" | "start-connects-end" | "end-connects-start":
                overlap_shift = None
            case "following":
                overlap_shift.start = other.start
            case "leading":
                overlap_shift.end = other.end
            case "contain" | "equal":
                overlap_shift = other
            case "be-contained":
                None
        return [compare_result, overlap_shift]

    def get_outer(self, other: "Shift") -> List["Shift"]:
        """Get the outer `Shift`s of 2 overlapped `Shift`s, return both of them, if not overlapped"""
        compare_result, overlap_shift = self.get_overlap(other)
        outer_shifts = [self]
        match compare_result:
            case "start-connects-end" | "end-connects-start":
                return [
                    Shift(
                        start=min(self.start, other.start), end=max(self.end, other.end)
                    )
                ]
            case "following":
                overlap_shift.start = other.start
            case "leading":
                overlap_shift.end = other.end
            case "contain" | "equal":
                overlap_shift = other

    def __ne__(self, other: "Shift") -> bool:
        """different than. No overlap at all"""
        return self > other or self < other

    def __gt__(self, other: "Shift") -> bool:
        """greater than"""
        return self.start > other.end

    def __lt__(self, other: "Shift") -> bool:
        """less than"""
        return self.end < other.start

    def __eq__(self, other: "Shift") -> bool:
        """equal to"""
        return self.start == other.start and self.end == other.end
