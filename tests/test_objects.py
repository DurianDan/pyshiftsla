from pysla.shift import Shift, SHIFT_STRING, COMPARE_TO_ANOTHER_SHIFT
from typing import Tuple, List

left_shift_str = "10101110"
RIGHT_SHIFTS_TO_COMPARE_STR: Tuple[
    COMPARE_TO_ANOTHER_SHIFT, List[SHIFT_STRING]
] = [
    ["greater", ["01101000"]],
    ["smaller", ["11201200"]],
    ["start-connects-end", ["09101010"]],
    ["end-connects-start", ["11101200"]],
    ["equal", ["10101110"]],
    ["following", ["11001200"]],
    ["leading", ["10001100"]],
    ["contain", ["10201100", "10201110", "10101100"]],
    ["be-contained", ["10001130", "10001110", "10101130"]],
]

LEFT_SHIFT = Shift.fromstr(left_shift_str)
RIGHT_SHIFTS_TO_COMPARE: Tuple[COMPARE_TO_ANOTHER_SHIFT, List[Shift]] = [
    [compare_result, [Shift.fromstr(shiftstr) for shiftstr in shiftstrs]]
    for [compare_result, shiftstrs] in RIGHT_SHIFTS_TO_COMPARE_STR
]
