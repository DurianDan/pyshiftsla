from datetime import date

from pysla.daterange import DateRange


TEST_YEAR = 2024
SOLAR_NEW_YEAR = date(TEST_YEAR, 1, 1)
US_INDEPENDENCE_DAY = date(TEST_YEAR, 7, 4)

VIETNAM_VICTORY_DAY = DateRange.fromstr(f"{TEST_YEAR}0430-{TEST_YEAR}0501")
VIETNAM_INDEPENDENCE_DAY = DateRange.fromstr(f"{TEST_YEAR}0902-{TEST_YEAR}0903")
VIETNAMESE_LUNAR_NEW_YEAR = DateRange.fromstr(
    f"{TEST_YEAR}0101-{TEST_YEAR}0105", calendar_type="lunar"
)
VIETNAM_HUNGS_KING_FESTIVAL = DateRange.fromstr(
    f"{TEST_YEAR}0310", calendar_type="lunar"
)
