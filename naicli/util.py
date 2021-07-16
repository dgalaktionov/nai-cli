from typing import TypeVar, Sequence, Callable, Optional

def join_strings(*strings: str) -> str:
    # when there's only a few of them, it's faster with fstrings (tested on Python 3.9)
    if len(strings) == 2:
        return f"{strings[0]}{strings[1]}"
    elif len(strings) == 3:
        return f"{strings[0]}{strings[1]}{strings[2]}"
    else:
        return "".join(strings)

TINDEX = TypeVar("TINDEX")
TVAL = TypeVar("TVAL")
def exponential_search(array: Sequence[TINDEX], value: TVAL, key: Optional[Callable[[TINDEX], TVAL]] = None, from_end = False):
    """
        Using exponential search over a sorted array, it returns the last (rightmost) position of a value using exponential search.
        If there is no such value in the array, a corresponding insertion position is returned.
        Analogous to bisect.bisect_right.
        Like with the function sorted, it is possible to provide a mapping function from the type of the array to the type of the value.
        When from_end is set, the search is performed starting from the end of the array (right-to-left).
    """
    if len(array) == 0: return 0
    if not key: key = lambda x: x
    
    i = 1
    start, end = 0, len(array)
    
    # exponential search phase
    if from_end:
        i = -1
        while -i < len(array) and key(array[i]) > value: i *= 2
        start, end = max(0, i+len(array)), len(array)-i//-2
    else:
        while i < len(array) and key(array[i]) <= value: i *= 2
        start, end = i//2, min(i+1, len(array))
   
    #binary search phase
    while start < end:
        i = (start+end)//2
        if value < key(array[i]): end = i
        else: start = i+1
    
    return start