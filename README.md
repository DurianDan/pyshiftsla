# pysla
    Highly customizable SLA calculator and Work shift Generator, for any time-keeping and days-off policies
---
### Quickstart - A case in Vietnam's Law:
- Let's calculate **SLA** and **generate work shifts** for an **American** female employee, Working in **Vietnam**, about to take maternity leave.
- Law references: [(1)][1]; [(2)][2]
#### 1. She will have:
- **4-month** of **maternity leave**.
- Holidays leave:
    - All **Vietnamese holidays**.
    - **1 day** from home country's **New Year**'s days (2024-01-01) (same as Solar New Year in Vietnam) (+0 holiday leave)
    - **1 day** from home country's Independence Days (2024-07-04) (+1 holiday leave)
- **Overtime shift** in the **Solar New Year**: from 13:30 to 14:30
- Plus random **3 days off**

#### 2. Configuration for `ShiftsBuilder`
```python
from pysla.shifts_builder import ShiftsBuilder, Shift, DateRange
from datetime import time, date

US_WOMAN_LIVING_IN_VIETNAM_MATERNITY_LEAVE_4MONTHS_2024 = ShiftsBuilder(
    workdays_weekly=[0,1,2,3,4], # weekday indexes: Monday to Friday
    daily_shifts=DailyShift([
        # Usual Morning shift: 8:30 to 11:45
        # Created using a string, easier to read but slower
        Shift.fromstr("08301145"),
        # Usual Afternoon shift: 13:30 to 18:00
        # Parsed the timestamps straight to parameters, faster
        Shift(start=time(13,30), end=time(18))
    ]),
    days_off_ranges=[ # you can parse `date` or `DateRange`
        date(2024, 1, 1), # SOLAR_NEW_YEAR
        date(2024, 7, 4), # US_INDEPENDENCE_DAY
        DateRange.fromstr("20240430-20240501"), #VIETNAM_VICTORY_DAY
        DateRange.fromstr("20240902-20240903"), #VIETNAM_INDEPENDENCE_DAY
        #VIETNAMESE_LUNAR_NEW_YEAR, Lunar DateRange will automatically turn into Solar DateRange
        DateRange.fromstr("20240101-20240105", calendar_type="lunar") 
        #VIETNAM_LUNAR_HUNG_KINGS_FESTIVAL
        DateRange.fromstr("20240310", calendar_type="lunar")

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
```

#### 3. Generate `ShiftRange` for year 2024
- `ShiftRange` works like a dictionary, and can check the generated `Shift` at a specific `date`.
```python
generated_shiftrange = ( # ShiftRange for 2024
    US_WOMAN_LIVING_IN_VIETNAM_MATERNITY_LEAVE_4MONTHS_2024
    .build_shifts_from_daterange(
        from_date=date(2024, 1, 1),
        to_date=date(2024, 12, 30))
    )
# Get Shifts in New Year 2024-01-01
generated_shiftrange[date(2024,1,1)] 
# [Shift(start=datetime.time(13, 30), end=datetime.time(14, 30))]

# Get Shifts in a random working day
generated_shiftrange[date(2024,2,8)]
# [
#   Shift(start=datetime.time(8, 30), end=datetime.time(11, 45)), 
#   Shift(start=datetime.time(13, 30), end=datetime.time(18, 0)) 
# ]

# Get Shifts in a day off (holiday leave) 2024-07-04
# KeyError: datetime.date(2024, 2, 9)
generated_shiftrange[date(2024,7,4)]
generated_shiftrange.get(date(2024,7,4)) # None
```

#### 4. Calculate SLA (service-level agreement)
- The result will be in `Milliseconds`:
```python
sla_millis = (
    US_WOMAN_lIVING_IN_VIETNAM_MATERNITY_LEAVE_4MONTHS_2024
    .calculate_sla(
        start_deal=datetime(2024, 1, 1, 14),
        end_deal=datetime(2024, 1, 2, 9, 30),
        use_generated_shifts=True, # for faster execution, 
        # reuse the cached results from `build_shifts_from_daterange`,
        # if "False", set re-generated `ShiftsRange` from `start_deal` to `end_deal`
    )
)
sla_hours = sla_millis/(1000*60*60) # 1.5 hours
```


### Global `ShiftsBuilder` config for your company/team
```python
from pysla.shifts_builder import ShiftsBuilder, Shift
from datetime import time

COMPANY_SHIFTS_BUILDER = ShiftsBuilder(
    daily_shifts=DailyShift([
        Shift.fromstr("08301145"), # morning shift, created using a string, easier to read but slower
        Shift(start=time(13,30), end=time(18)) # afternoon shift, parsed the timestamps straight to parameters, faster
    ]),
    workdays_weekly=[0,1,2,3,4] # Monday to Friday
)
```
- Copy config to a specific `employee`.
```python
employee_takes_4_days_off = (
    COMPANY_SHIFTS_BUILDER
    .add_days_off_range(
        [
            DateRange.fromstr("20241204-20241205"), # 2days off
            DateRange.fromstr("20241000-20241001") # 2days off
        ],
        inplace=False # if `False` will return a copied `ShiftsBuilder`,
        # if `True`, will change `COMPANY_SHIFTS_BUILDER` and return `None`
    ))
```


[1]:https://english.luatvietnam.vn/legal-news/public-holiday-leaves-of-foreign-employees-in-vietnam-4729-91710-article.html
[2]: https://vietnamlawmagazine.vn/maternity-leave-for-foreign-female-employees-6115.html