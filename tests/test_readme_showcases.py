from pyshiftsla.shifts_builder import (
    ShiftsBuilder,
    DateRange,
    DailyShift,
    ShiftRange,
)
from pyshiftsla.shift import Shift
from datetime import time, date, datetime
import pytest


def test_readme_first_showcase_us_woman():
    US_WOMAN_LIVING_IN_VIETNAM_MATERNITY_LEAVE_4MONTHS_2024 = ShiftsBuilder(
        workdays_weekly=[0, 1, 2, 3, 4],  # weekday indexes: Monday to Friday
        daily_shifts=DailyShift(
            [
                # Usual Morning shift: 8:30 to 11:45
                # Created using a string, easier to read but slower
                Shift.fromstr("08301145"),
                # Usual Afternoon shift: 13:30 to 18:00
                # Parsed the timestamps straight to parameters, faster
                Shift(start=time(13, 30), end=time(18)),
            ]
        ),
        days_off_ranges=[  # you can parse `date` or `DateRange`
            date(2024, 1, 1),  # SOLAR_NEW_YEAR
            date(2024, 7, 4),  # US_INDEPENDENCE_DAY
            DateRange.fromstr("20240430-20240501"),  # VIETNAM_VICTORY_DAY
            DateRange.fromstr("20240902-20240903"),  # VIETNAM_INDEPENDENCE_DAY
            # VIETNAMESE_LUNAR_NEW_YEAR,
            # Lunar DateRange will automatically turn into Solar DateRange
            DateRange.fromstr("20240101-20240105", calendar_type="lunar"),
            # VIETNAM_LUNAR_HUNG_KINGS_FESTIVAL
            DateRange.fromstr("20240310", calendar_type="lunar"),
            # 4 months of maternity leave
            DateRange.fromstr("20240801-20241201"),
            date(2024, 2, 9),  # custom days off
            date(2024, 6, 3),  # custom days off
            date(2024, 12, 10),  # custom days off
        ],
        special_shifts=ShiftRange(
            {
                # Urgent overtime in the Solar New Year
                # 13:30 to 14:30
                date(2024, 1, 1): DailyShift([Shift.fromstr("13301430")]),
            }
        ),
    )
    generated_shiftrange = (  # ShiftRange for 2024
        US_WOMAN_LIVING_IN_VIETNAM_MATERNITY_LEAVE_4MONTHS_2024.build_shifts_from_daterange(
            from_date=date(2024, 1, 1), to_date=date(2024, 12, 30)
        )
    )
    # Get Shifts in New Year 2024-01-01
    new_years_date = generated_shiftrange[date(2024, 1, 1)]
    assert new_years_date.get_shifts_num() == 1
    assert (
        new_years_date[0].compare(Shift(start=time(13, 30), end=time(14, 30)))
        == "equal"
    )

    random_working_day = generated_shiftrange[date(2024, 2, 8)]
    assert random_working_day.get_shifts_num() == 2
    assert (
        random_working_day[0].compare(
            Shift(start=time(8, 30), end=time(11, 45))
        )
        == "equal"
    )
    assert (
        random_working_day[1].compare(
            Shift(start=time(13, 30), end=time(18, 0))
        )
        == "equal"
    )

    # Get Shifts in a day off (holiday leave) 2024-07-04
    with pytest.raises(KeyError):
        # KeyError: datetime.date(2024, 7, 4)
        generated_shiftrange[date(2024, 7, 4)]
    assert generated_shiftrange.get(date(2024, 7, 4)) is None


def test_readme_second_showcase_us_woman_sla():
    US_WOMAN_LIVING_IN_VIETNAM_MATERNITY_LEAVE_4MONTHS_2024 = ShiftsBuilder(
        workdays_weekly=[0, 1, 2, 3, 4],  # weekday indexes: Monday to Friday
        daily_shifts=DailyShift(
            [
                # Usual Morning shift: 8:30 to 11:45
                # Created using a string, easier to read but slower
                Shift.fromstr("08301145"),
                # Usual Afternoon shift: 13:30 to 18:00
                # Parsed the timestamps straight to parameters, faster
                Shift(start=time(13, 30), end=time(18)),
            ]
        ),
        days_off_ranges=[  # you can parse `date` or `DateRange`
            date(2024, 1, 1),  # SOLAR_NEW_YEAR
            date(2024, 7, 4),  # US_INDEPENDENCE_DAY
            DateRange.fromstr("20240430-20240501"),  # VIETNAM_VICTORY_DAY
            DateRange.fromstr("20240902-20240903"),  # VIETNAM_INDEPENDENCE_DAY
            # VIETNAMESE_LUNAR_NEW_YEAR,
            # Lunar DateRange will automatically turn into Solar DateRange
            DateRange.fromstr("20240101-20240105", calendar_type="lunar"),
            # VIETNAM_LUNAR_HUNG_KINGS_FESTIVAL
            DateRange.fromstr("20240310", calendar_type="lunar"),
            # 4 months of maternity leave
            DateRange.fromstr("20240801-20241201"),
            date(2024, 2, 9),  # custom days off
            date(2024, 6, 3),  # custom days off
            date(2024, 12, 10),  # custom days off
        ],
        special_shifts=ShiftRange(
            {
                # Urgent overtime in the Solar New Year
                # 13:30 to 14:30
                date(2024, 1, 1): DailyShift([Shift.fromstr("13301430")]),
            }
        ),
    )
    sla_millis = (
        US_WOMAN_LIVING_IN_VIETNAM_MATERNITY_LEAVE_4MONTHS_2024.calculate_sla(
            start_deal=datetime(2024, 1, 1, 14),
            end_deal=datetime(2024, 1, 2, 9, 30),
            use_generated_shifts=True,  # for faster execution,
            # reuse the cached results from `build_shifts_from_daterange`,
            # if "False", set re-generated `ShiftsRange` from `start_deal` to `end_deal`
        )
    )
    assert sla_millis / (1000 * 60 * 60) == 1.5


def test_readme_third_showcase_global_shift_builder():
    COMPANY_SHIFTS_BUILDER = ShiftsBuilder(
        daily_shifts=DailyShift(
            [
                Shift.fromstr(
                    "08301145"
                ),  # morning shift, created using a string, easier to read but slower
                Shift(
                    start=time(13, 30), end=time(18)
                ),  # afternoon shift, parsed the timestamps straight to parameters, faster
            ]
        ),
        workdays_weekly=[0, 1, 2, 3, 4],  # Monday to Friday
    )
    employee_takes_4_days_off = COMPANY_SHIFTS_BUILDER.add_days_off_range(
        [
            DateRange.fromstr("20241204-20241205"),  # 2days off
            DateRange.fromstr("20240930-20241001"),  # 2days off
        ],
        inplace=False,  # if `False` will return a copied `ShiftsBuilder`,
        # if `True`, will change `COMPANY_SHIFTS_BUILDER` and return `None`
    )
    assert len(COMPANY_SHIFTS_BUILDER.days_off_ranges) == 0
    assert employee_takes_4_days_off is not None
    assert len(employee_takes_4_days_off.days_off_ranges) == 2
    assert employee_takes_4_days_off.days_off_ranges[0].dates == [
        date(2024, 12, 4),
        date(2024, 12, 5),
    ]
    assert employee_takes_4_days_off.days_off_ranges[1].dates == [
        date(2024, 9, 30),
        date(2024, 10, 1),
    ]
