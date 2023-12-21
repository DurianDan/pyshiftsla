from datetime import date

from tests.test_objects.manual import TEST_YEAR
from tests.test_objects.shifts_builder import (
    US_WOMAN_lIVING_IN_VIETNAM_MATERNITY_LEAVE_6MONTHS_2024,
)


def test_shifts_builder():
    US_WOMAN_lIVING_IN_VIETNAM_MATERNITY_LEAVE_6MONTHS_2024.build_shifts_from_daterange(
        from_date=date(TEST_YEAR, 1, 1), to_date=date(TEST_YEAR, 12, 30)
    )
