from pysla.common_daysoff import COMMON_DAILY_SHIFTS, COMMON_WORKDAYS_IN_WEEK
from pysla.shifts_builder import ShiftsBuilder
from pysla.shiftrange import ShiftRange
from pysla.daily_shifts import DailyShift
from pysla.daterange import DateRange
from pysla.shift import Shift

from datetime import date

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
US_WOMAN_lIVING_IN_VIETNAM_PREGNANT_LEAVE_6MONTHS_PARTTIME_2024 = (
    COMPANY_SHIFTS_BUILDER.partial_config_copy(
        days_off_ranges=[
            date(2024, 7, 4),  # US National Day/Independence Day
            date(2024, 1, 1),  # Solar New Year
            DateRange.fromstr("20240430-20230501"),  # Vietname Victory day
            DateRange.fromstr(
                "20240902-20230903"
            ),  # Vietnam National Day/Independence Day
            DateRange.fromstr(
                "20240101-20240105", calendar_type="lunar"
            ),  # Vietnamese Lunar New Year
            DateRange.fromstr(
                "20240310", calendar_type="lunar"
            ),  # Vietnamese Hungs King Festival]
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
    print(
        US_WOMAN_lIVING_IN_VIETNAM_PREGNANT_LEAVE_6MONTHS_PARTTIME_2024.get_days_off()
    )
