from datetime import date, datetime

from tests.test_objects.manual import TEST_YEAR
from tests.test_objects.shifts_builder import (
    US_WOMAN_lIVING_IN_VIETNAM_MATERNITY_LEAVE_6MONTHS_2024,
)


def test_shifts_builder():
    US_WOMAN_lIVING_IN_VIETNAM_MATERNITY_LEAVE_6MONTHS_2024.build_shifts_from_daterange(
        from_date=date(TEST_YEAR, 1, 1), to_date=date(TEST_YEAR, 12, 30)
    )
    millis_sla_new_year_day = (
        US_WOMAN_lIVING_IN_VIETNAM_MATERNITY_LEAVE_6MONTHS_2024.calculate_sla(
            start_deal=datetime(TEST_YEAR, 1, 1, 14),
            end_deal=datetime(TEST_YEAR, 1, 2, 9, 30),
            use_generated_shifts=True,
        )
    )
    hours_sla_new_year_day = millis_sla_new_year_day / (1000 * 60 * 60)
    assert (
        hours_sla_new_year_day == 1.5
    ), f"hours_sla_new_year_day should be 1.5, not {hours_sla_new_year_day}"
