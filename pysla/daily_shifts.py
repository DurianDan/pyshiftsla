from pydantic import AfterValidator, RootModel
from typing import Annotated, List, Literal, Dict, Tuple
from datetime import datetime
from .datetime_utilities import Milliseconds
from .shift import Shift, RESOLVED_TWO_SHIFTS

RESOLVE_SHIFTS_METHOD = Literal[
    "overlapped", "outer", "throw-error", "delete-both"
]

SORTED_SHIFTS_START = Annotated[
    List[Shift], AfterValidator(lambda x: sorted(x, key=lambda y: y.start))
]


class DailyShift(RootModel):
    """
    Shifts in a day, represented by a list of `Shift` objects,
     these `Shift`s are not overlapped and
     have the total milliseconds smaller than or equal to a day
     (1day = 24hours = 24*60*60*1000Milliseconds)
    """

    root: List[Shift]

    def __iter__(self) -> List[Shift]:
        return self.root

    def __getitem__(self, idx: int) -> Shift | None:
        if not isinstance(idx, int):
            raise NotImplementedError(
                f"Only accept index as `int` not {type(idx)}"
            )
        return self.root[idx]

    @classmethod
    def sorted_shifts_start(cls, shifts: List[Shift]) -> SORTED_SHIFTS_START:
        sorted_shifts = sorted(shifts, key=lambda x: x.start)
        return sorted_shifts

    @classmethod
    def resolve_overlap_shifts(
        cls, shifts: List[Shift], method: RESOLVE_SHIFTS_METHOD = "throw-error"
    ) -> "DailyShift":
        sorted_shifts = cls.sorted_shifts_start(shifts)
        resolved = []

        for idx, (tmp_shift, tmp_next_shift) in enumerate(
            zip(sorted_shifts, sorted_shifts[1:])
        ):
            tmp_resolve = tmp_shift.resolve(tmp_next_shift)
            if tmp_shift is None:
                continue
            match method, tmp_resolve["compare_result"]:
                case _, "smaller" | "greater":
                    resolved.append(tmp_shift)
                case "delete-both", _:
                    sorted_shifts[idx + 1] = None
                case "throw-error", _:
                    raise ValueError(
                        f"overlap Shifts:\n+ At index {idx}: \
                        {tmp_shift}\n + At index {idx+1}: {tmp_next_shift}"
                    )
                case _, "overlapped" | "outer":
                    (
                        sorted_shifts,
                        resolved,
                    ) = cls.resolve_overlapped_outer_shifts(
                        tmp_resolve, method, sorted_shifts, resolved
                    )
        recheck_overlapped_shifts = cls.check_overlap_shifts(resolved)
        assert (
            len(recheck_overlapped_shifts) == 0
        ), f"Tried resolving, cant resolved these `Shift`s: {recheck_overlapped_shifts}"
        return DailyShift(resolved)

    @staticmethod
    def resolve_overlapped_outer_shifts(
        tmp_resolve: RESOLVED_TWO_SHIFTS,
        method: Literal["overlapped", "outer"],
        sorted_original_shifts: SORTED_SHIFTS_START,
        sorted_resolving_shifts: SORTED_SHIFTS_START,
        tmp_shift_idx: int,
    ) -> Tuple[SORTED_SHIFTS_START, SORTED_SHIFTS_START]:
        match method:
            case "outer":
                sorted_resolving_shifts.append(tmp_resolve[method][0])
                sorted_original_shifts[tmp_shift_idx + 1] = tmp_resolve[method][1]
            case "overlapped":
                sorted_resolving_shifts.append(tmp_resolve[method])
                sorted_resolving_shifts[tmp_shift_idx + 1] = tmp_resolve[method]
        return sorted_original_shifts, sorted_resolving_shifts

    @classmethod
    def check_overlap_shifts(
        cls, shifts: List[Shift], sorted_starts: bool = True
    ) -> Dict[int, List[Shift]]:
        overlapped = {}
        sorted_shifts = (
            shifts if sorted_starts else cls.sorted_shifts_start(shifts)
        )
        for idx, tmp_shift in enumerate(sorted_shifts[:-1]):
            next_tmp_shift = sorted_shifts[idx + 1]
            if not tmp_shift != next_tmp_shift:
                continue
            overlapped[idx] = [tmp_shift, next_tmp_shift]
        return overlapped

    def total_milliseconds(self) -> Milliseconds:
        return sum([shift.diff for shift in self])

    def work_amount_in_shifts(
        self, start_work: datetime, end_work: datetime
    ) -> Milliseconds:
        pass
