from typing import List, Optional, Literal, Union, Tuple, TypedDict
from pydantic import BaseModel, model_validator, AfterValidator
from typing_extensions import Annotated
from datetime import time
from .datetime_utilities import (
    diff_time,
    check_start_end_event,
    compare_times,
    Milliseconds,
)

COMPARE_TO_ANOTHER_SHIFT_MISMATCH_STARTEND = (
    Literal[  # comparing -___- to |___|
        "smaller",  # -___-  |___|
        "greater",  # |___|  -___-
        "end-connects-start",  # -___+___|
        "start-connects-end",  # |___+___-
    ]
)
COMPARE_TO_ANOTHER_SHIFT_MATCH_STARTEND = Literal[  # comparing -___- to |___|
    "equal",  # +___+
    "following",  # -_|__-_|
    "leading",  # |_-__|_-
    "contain",  # -__|__|__-
    "be-contained",  # |__-__-__|
]
COMPARE_TO_ANOTHER_SHIFT = Union[
    COMPARE_TO_ANOTHER_SHIFT_MISMATCH_STARTEND,
    COMPARE_TO_ANOTHER_SHIFT_MATCH_STARTEND,
]


class RESOLVED_OVERLAPPED_SHIFT(TypedDict):
    overlapped: Optional["Shift"]
    compare_result: COMPARE_TO_ANOTHER_SHIFT


RESOLVED_OUTER_SHIFTS = Optional[
    List["Shift"]
]  # `None` if 2 `Shift`s are equal


class RESOLVED_TWO_SHIFTS(RESOLVED_OVERLAPPED_SHIFT):
    outer: RESOLVED_OUTER_SHIFTS


def check_shift_str(shiftstr: str) -> str:
    assert (
        len(shiftstr) == 8
    ), f"Shift string must have length 8, not {len(shiftstr)}, {shiftstr = }"
    assert (
        shiftstr.isnumeric()
    ), f"Shift string must contains only numbers: {shiftstr = }"
    return shiftstr


def convert_shift_str(shiftstr: str) -> Tuple[time, time] | None:
    nums = [int(shiftstr[i : i + 2]) for i in range(0, 8, 2)]
    try:
        first_time = time(nums[0], nums[1])
        second_time = time(nums[2], nums[3])
        return [first_time, second_time]
    except Exception as err:
        raise Exception(f"Invalid `shiftstr` {shiftstr}") from err


SHIFT_STRING = Annotated[str, AfterValidator(check_shift_str)]


class Shift(BaseModel):
    start: time
    end: time

    @model_validator(mode="after")
    def start_must_happend_before_end(self) -> "Shift":
        check_start_end_event(self.start, self.end)
        return self

    @classmethod
    def fromstr(cls, shiftstr: SHIFT_STRING) -> "Shift":
        """Turn a string into a Shift.
        E.g.: "01120932" => Shift(start=time(1,12), end=time(9,32))
        """
        checked_shiftstr = convert_shift_str(shiftstr)
        return Shift(start=checked_shiftstr[0], end=checked_shiftstr[1])

    @property
    def diff(self) -> Milliseconds:
        return diff_time(self.start, self.end)

    def is_in_shift(self, event: time) -> bool:
        return event >= self.start and event <= self.end

    def work_amount_in_shift(
        self, start_work: time, end_work: time
    ) -> Milliseconds:
        """
        Calculate how much a work takes up a shift.
        return the milliseconds(int) that work takes

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
                if start_work < self.start and end_work > self.end:
                    # if shift is between the start and end work
                    return self.diff
                # if there's no shift between start and end work
                return 0

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
            case "equal", "equal":  # equal
                return "equal"
            case "smaller", "smaller":  # following
                return "following"
            case "greater", "greater":  # leading
                return "leading"
            case "equal", "greater":  # contain
                return "contain"
            case "smaller", "equal" | "greater":
                return "contain"
            case "equal", "smaller":  # be-contained
                return "be-contained"
            case "greater", "smaller" | "equal":
                return "be-contained"

    def compare(self, other: "Shift") -> COMPARE_TO_ANOTHER_SHIFT:
        compare_mismatch_startend = self._compare_mismatch_startend(other)
        if compare_mismatch_startend:
            return compare_mismatch_startend
        return self._compare_match_startend(other)

    def get_overlap(self, other: "Shift") -> RESOLVED_OVERLAPPED_SHIFT:
        """Get overlapped `Shift`. if not overlap => return None."""
        overlapped_shift = Shift(  # equal to self `Shift`
            start=self.start, end=self.end
        )
        compare_result = self.compare(other)
        match compare_result:
            case (
                "smaller"
                | "greater"
                | "start-connects-end"
                | "end-connects-start"
            ):
                overlapped_shift = None
            case "following":
                overlapped_shift.start = other.start
            case "leading":
                overlapped_shift.end = other.end
            case "contain":
                overlapped_shift = other
        return {
            "overlapped": overlapped_shift,
            "compare_result": compare_result,
        }

    def get_outer(
        self,
        other: "Shift",
        resovled_overlap: RESOLVED_OVERLAPPED_SHIFT | None = None,
    ) -> RESOLVED_OUTER_SHIFTS:
        """Get the outer `Shift`s of 2 overlapped `Shift`s,
        return both of them, if not overlapped
        """
        if resovled_overlap is None:
            resovled_overlap = self.get_overlap(other)
        outer_shifts = [self]
        match resovled_overlap["compare_result"]:
            case "smaller" | "greater":
                outer_shifts.append(other)
            case "end-connects-start" | "start-connects-end":
                outer_shifts = [
                    Shift(
                        start=min([self.start, other.start]),
                        end=max([self.start, other.end]),
                    )
                ]
            case "equal":
                outer_shifts = None
            case "following" | "leading" | "contain" | "be-contained":
                outer_shifts = [
                    Shift(
                        start=min([self.start, other.start]),
                        end=resovled_overlap["overlapped"].start,
                    ),
                    Shift(
                        start=resovled_overlap["overlapped"].end,
                        end=max([self.end, other.end]),
                    ),
                ]
        return outer_shifts

    def resolve(self, other: "Shift") -> RESOLVED_TWO_SHIFTS:
        """Check if 2 shifts are overlap, and overlap how much with each other.
        :param other: the other `Shift` to compare to
        :param strategy: default is 'inner' means getting the overlapped `Shift`,
            or None if no overllaped.
            'outer' is for getting the outer join of the 2 Shifts,
            return a list of outer `Shift`s (overlapped Shift not included)';
            'both' will return both 'outer' and 'inner' resolving results.
        :rtype:  `RESOLVED_TWO_SHIFTS`
        """
        resolved_overlap = self.get_overlap(other)
        resolved = {
            **resolved_overlap,
            "outer": self.get_outer(other, resolved_overlap),
        }
        return resolved

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
