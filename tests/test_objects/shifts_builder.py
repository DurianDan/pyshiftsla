from pysla.common_daysoff import COMMON_DAILY_SHIFTS, COMMON_WORKDAYS_IN_WEEK
from pysla.shifts_builder import ShiftsBuilder
from pysla.shiftrange import ShiftRange
from pysla.daily_shifts import DailyShift
from pysla.daterange import DateRange
from pysla.shift import Shift

from tests.test_objects.manual import (
    SOLAR_NEW_YEAR,
    US_INDEPENDENCE_DAY,
    VIETNAM_VICTORY_DAY,
    VIETNAM_INDEPENDENCE_DAY,
    VIETNAMESE_LUNAR_NEW_YEAR,
    VIETNAM_HUNG_KINGS_FESTIVAL,
)

from datetime import date, datetime

COMPANY_SHIFTS_BUILDER = ShiftsBuilder(
    # from 8:30 to 11:45
    # from 13:30 to 18:00
    daily_shifts=COMMON_DAILY_SHIFTS,
    # Monday to Friday
    workdays_weekly=COMMON_WORKDAYS_IN_WEEK,
)

"""Test case 1: A US female citizen living in a Vietnam working for a company, about to give birth.
- Having 4-month of maternity leave
- Holidays leave:
    - All Vietnamese holidays.
    - 1 day from home country's New Year's days (2024-01-01) (same as Solar New Year in Vietnam)
    - 1 day from home country's Independence Days (2024-07-04) (+1 holiday leave)
- Overtime work in the Solar New Year: from 13:30 to 14:30
"""
US_WOMAN_lIVING_IN_VIETNAM_MATERNITY_LEAVE_4MONTHS_2024 = (
    COMPANY_SHIFTS_BUILDER.partial_config_copy(
        days_off_ranges=[
            SOLAR_NEW_YEAR,
            US_INDEPENDENCE_DAY,
            VIETNAM_VICTORY_DAY,
            VIETNAM_INDEPENDENCE_DAY,
            VIETNAMESE_LUNAR_NEW_YEAR,
            VIETNAM_HUNG_KINGS_FESTIVAL,
            DateRange.fromstr(
                "20240801-20241201"
            ),  # 4 months of maternity leave
            date(2024, 2, 9),  # custom days off
            date(2024, 6, 3),  # custom days off
            date(2024, 12, 10),  # custom days off
        ],
        # parttime at month
        special_shifts=ShiftRange(
            {
                # urgent work overtime in the Solar New Year
                # 13:30 to 14:30
                date(2024, 1, 1): DailyShift([Shift.fromstr("13301430")]),
            }
        ),
    )
)

if __name__ == "__main__":
    from icecream import ic

    # ic(
    #     US_WOMAN_lIVING_IN_VIETNAM_MATERNITY_LEAVE_4MONTHS_2024.get_days_off()
    # )
    US_WOMAN_lIVING_IN_VIETNAM_MATERNITY_LEAVE_4MONTHS_2024.build_shifts_from_daterange(
        from_date=date(2024, 1, 1), to_date=date(2024, 12, 30)
    )
    generated_shifts = US_WOMAN_lIVING_IN_VIETNAM_MATERNITY_LEAVE_4MONTHS_2024.get_generated_shifts()

    ic(generated_shifts[date(2024, 1, 2)])
    ic(generated_shifts[date(2024, 1, 2)].total_milliseconds / (1000 * 3600))

    ic(
        US_WOMAN_lIVING_IN_VIETNAM_MATERNITY_LEAVE_4MONTHS_2024.calculate_sla(
            start_deal=datetime(2024, 1, 1, 14, 0),
            end_deal=datetime(2024, 1, 3, 9, 30),
            use_generated_shifts=True,
        )
        / (1000 * 3600)
    )
