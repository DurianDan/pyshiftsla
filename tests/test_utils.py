from datetime import date
from typing import List, Literal
import random

DAYS_IDX_ORDER = Literal["ascending", "descending", "random"]


def generate_days_idx(strategy: DAYS_IDX_ORDER) -> List[int]:
    match strategy:
        case "ascending":
            return list(range(1, 32))
        case "descending":
            return list(range(31, 0, -1))
        case "random":
            return random.sample(range(1, 13), k=12)


def generate_monthly_days_off(
    year: int,
    workdays_weekly: List[int] = [0, 1, 2, 3, 4],
    days_idx_order: DAYS_IDX_ORDER = "ascending",
) -> List[date]:
    """
    Generate a list of random dates between 1st and 31st of the each of 12 months.
    These dates will always be weekdays specified by `workdays_weekly`
    """
    days_off = [None] * 12
    months_idx = generate_days_idx(days_idx_order)
    random.sample(range(1, 32), k=31)
    for month in range(1, 13):
        for day in months_idx:
            try:
                tmp_date = date(year, month, day)
            except ValueError:
                continue
            if tmp_date.weekday() in workdays_weekly:
                days_off[month - 1] = tmp_date
                break
    return days_off


if __name__ == "__main__":
    print(generate_monthly_days_off(2024, [0, 1, 2, 3, 4], "descending"))
