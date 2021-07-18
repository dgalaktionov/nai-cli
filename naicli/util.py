from typing import TypeVar, Sequence, Callable, Optional
from operator import gt

def join_strings(*strings: str) -> str:
    # when there's only a few of them, it's faster with fstrings (tested on Python 3.9)
    if len(strings) == 2:
        return f"{strings[0]}{strings[1]}"
    elif len(strings) == 3:
        return f"{strings[0]}{strings[1]}{strings[2]}"
    else:
        return "".join(strings)

def find_nth(s, x, n=0, overlap=False):
    # shamelessly copied from Stefan in https://stackoverflow.com/a/23479065
    l = 1 if overlap else len(x)
    i = -l
    for c in range(n + 1):
        i = s.find(x, i + l)
        if i < 0:
            break
    return i

T = TypeVar("T")
def exponential_search(array: Sequence[T], value: T, comparator=gt, from_end = False):
    """
        Using exponential search over a sorted array, it returns the last (rightmost) position of a value using exponential search.
        If there is no such value in the array, a corresponding insertion position is returned.
        Analogous to bisect.bisect_right.
        By passing comparator=operator.ge it becomes equivalent to bisect.bisect_left
    """
    if len(array) == 0: return 0
    
    i = 1
    start, end = 0, len(array)
    
    # exponential search phase
    if from_end:
        i = -1
        while -i < len(array) and comparator(array[i], value): i *= 2
        start, end = max(0, i+len(array)), len(array)-i//-2
        if start > 0: start += 1
    else:
        while i < len(array) and not comparator(array[i], value): i *= 2
        start, end = i//2, min(i+1, len(array))
        if start > 0: start += 1
    
    #binary search phase
    while start < end:
        i = (start+end)//2
        if comparator(array[i], value): end = i
        else: start = i+1
    
    return start