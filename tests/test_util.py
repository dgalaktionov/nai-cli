import pytest

from hypothesis import given
from hypothesis.strategies import text, lists

from typing import List

from naicli.util import *

@given(lists(text()))
def test_join_strings(strings: List[str]):
    assert "".join(strings) == join_strings(*strings)