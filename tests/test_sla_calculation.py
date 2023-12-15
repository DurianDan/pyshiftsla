import pytest
from pprint import pprint
from pysla.shifts_builder import ShiftsBuilder, DailyShift


def test_default_shiftsbuilder():
    default = ShiftsBuilder()
    pprint(default.shifts_daily)
    assert isinstance(default.shifts_daily, DailyShift)
