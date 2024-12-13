from datetime import date, datetime, time
from pyshiftsla.shifts_builder import ShiftsBuilder, DailyShift, ShiftRange
from pyshiftsla.shift import Shift


def test_default_shiftsbuilder():
    default = ShiftsBuilder()
    assert isinstance(default.daily_shifts, DailyShift)


def test_calculate_sla_on_days_with_no_shifts():
    builder = ShiftsBuilder(
        workdays_weekly=[0, 1, 2, 3, 4],
        daily_shifts=DailyShift(
            [
                Shift(start=time(8, 30), end=time(11, 45)),
                Shift(start=time(13, 30), end=time(18, 00)),
            ]
        ),
        days_off_ranges=[date(2024, 12, 13)],  # Leave on Friday
    )
    resolution_time = builder.calculate_sla(
        start_deal=datetime(2024, 12, 13, 11, 30),
        end_deal=datetime(2024, 12, 16, 10, 30),  # Monday
    )
    expected_sla = 2 * 60 * 60 * 1000  # 2 hours
    assert resolution_time == expected_sla
