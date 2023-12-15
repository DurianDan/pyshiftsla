import pytest

from pysla.shift import Shift
from pysla.common_daysoff import COMMON_DAILY_SHIFTS
from pysla.shift import COMPARE_TO_ANOTHER_SHIFT

from typing import Tuple, List
from datetime import time

from .test_objects import LEFT_SHIFT, RIGHT_SHIFTS_TO_COMPARE


def test_COMMON_DAILY_SHIFTS():
    first_shift = COMMON_DAILY_SHIFTS[0]
    second_shift = COMMON_DAILY_SHIFTS[1]
    resolved_shifts = first_shift.resolve(second_shift)

    assert isinstance(
        first_shift, Shift
    ), f"Not an instance of Shift: {first_shift =}"
    assert resolved_shifts["compare_result"] == "smaller", (
        "COMMON_DAILY_SHIFTS > first shift must be 'smaller' than second shift, not "
        + resolved_shifts["compare_result"]
    )
    assert resolved_shifts["outer"] == [
        first_shift,
        second_shift,
    ], f"COMMON_DAILY_SHIFTS > outer shifts must be {[first_shift, second_shift]}, not {resolved_shifts['outer']}"


def test_shift_from_str():
    shiftstr = "10101110"
    shift_from_str = Shift.fromstr(shiftstr)
    result_shift = Shift(start=time(10, 10), end=time(11, 10))
    assert (
        shift_from_str == result_shift
    ), f"Wrong conversion from shift string '{shiftstr}' into '{shift_from_str}'"


def test_compare_two_shifts():
    for compare_result, right_shifts in RIGHT_SHIFTS_TO_COMPARE:
        for right_shift in right_shifts:
            tmp_comparison = LEFT_SHIFT.compare(right_shift)
            assert (
                tmp_comparison == compare_result
            ), f"Comparison '{compare_result}', wrong result: '{tmp_comparison}', {LEFT_SHIFT = }, {right_shift = }"


def test_resolve():
    pass
