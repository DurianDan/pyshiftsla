import pytest
from pysla.shifts_builder import ShiftsBuilder, DailyShift


def test_default_shiftsbuilder():
    default = ShiftsBuilder()
    assert isinstance(default.shifts_daily, DailyShift)
