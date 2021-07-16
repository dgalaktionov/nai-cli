import pytest
import bisect

from hypothesis import given, assume
from hypothesis.strategies import text, lists, integers, tuples

from typing import List, Tuple

from naicli.util import *

@given(lists(text()))
def test_join_strings(strings: List[str]):
    assert "".join(strings) == join_strings(*strings)

def _i100():
    return integers(min_value=-100, max_value=100)

@given(lists(_i100()).map(sorted), _i100())
def test_exponential_search(array: List[int], value: int):
    assume(len(array) > 0)
    assert exponential_search(array, value) == exponential_search(array, value, from_end=True) == bisect.bisect_right(array, value)
    
    for _ in range(4):
        bisect.insort(array, value)
        assert exponential_search(array, value) == exponential_search(array, value, from_end=True) == bisect.bisect_right(array, value)

@given(lists(tuples(_i100(), _i100())), _i100())
def test_exponential_key_search(array: List[Tuple[int,int]], value: int):
    assume(len(array) > 0)
    key = lambda a: a[1]
    array = sorted(array, key=key)
    mapped_array = list(map(key, array))
    assert exponential_search(array, value, key=key) == exponential_search(array, value, key=key, from_end=True) \
        == bisect.bisect_right(mapped_array, value)