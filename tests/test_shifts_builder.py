from datetime import date
from tests.test_objects.shifts_builder import (
    US_WOMAN_lIVING_IN_VIETNAM_MATERNITY_LEAVE_6MONTHS_2024,
)


def test_shifts_builder():
    US_WOMAN_lIVING_IN_VIETNAM_MATERNITY_LEAVE_6MONTHS_2024.build_shifts_from_daterange(
        from_date=date(2024, 1, 1), to_date=date(2024, 12, 30)
    )
