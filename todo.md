- [X] `Shift`;
    - Refactor the compare method to be Single-res
    - finish method resolve()
- [X]`DailyShift`:
    - add resolve() method for overlapping `Shift`
    - add validation for `Shift`s to be under **24hours**.
- [ ] `ShiftsBuilder`:
    - [ ] Generate `DailyShift` with **parsed configuration**:
        - [ ] Two generators:
            - [X] for a **range of dates**
            - [ ] for a **duration of hours**
    - [X] Validation if the **parsed parameters** are sufficient to generate **Shifts/SLA**
- [ ] Write tests for `ShiftsBuilder` > `build_shifts_from_daterange` and `calculate_sla`
- [ ] `ShiftsBuilder` > export `Shifts` into [*iCalendar*][1] file type


[1]: https://support.google.com/calendar/answer/37111?hl=en