import pytest

from pysla.shift import Shift
from pysla.common_daysoff import COMMON_DAILY_SHIFTS


def test_shift_resolve():
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
