from pysla.common_daysoff import COMMON_WORKDAYS_IN_WEEK
from tests.test_objects.manual import TEST_YEAR
from tests.test_utils import generate_monthly_days_off

DAYSOFF_AT_FIRST_WORKDAYS_EACH_MONTH = generate_monthly_days_off(
    year=TEST_YEAR,
    workdays_weekly=COMMON_WORKDAYS_IN_WEEK,
    days_idx_order="ascending",
    # 2024-01-1
    # 2024-02-1
    # 2024-03-1
    # 2024-04-1
    # 2024-05-1
    # 2024-06-11
    # 2024-07-1
    # 2024-08-1
    # 2024-09-11
    # 2024-10-1
    # 2024-11-1
    # 2024-12-11
)

DAYSOFF_AT_LAST_WORKDAYS_EACH_MONTH = generate_monthly_days_off(
    year=TEST_YEAR,
    workdays_weekly=COMMON_WORKDAYS_IN_WEEK,
    days_idx_order="descending",
    # 2024-01-31
    # 2024-02-29
    # 2024-03-29
    # 2024-04-30
    # 2024-05-31
    # 2024-06-28
    # 2024-07-31
    # 2024-08-30
    # 2024-09-30
    # 2024-10-31
    # 2024-11-29
    # 2024-12-31
)
