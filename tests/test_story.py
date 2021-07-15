import pytest

from naicli.story_model import *
from naicli.story import *

from hypothesis import given, assume
from hypothesis.strategies import integers

@pytest.fixture(scope="module")
def book():
    return open_story_file("example/grug.story")

@pytest.fixture(scope="module")
def full_text(book):
    return assemble_story_fragments(book.content.story.fragments)

@pytest.fixture(scope="module")
def story(book):
    return book.content.story
    
@pytest.fixture(scope="module")
def fragments(story):
    return story.fragments

@pytest.fixture(scope="module")
def fragment_delimiters(fragments):
    return list(accumulate(map(lambda f: len(f.data), fragments)))

def test_book(book):
    assert isinstance(book, Book)
    assert len(book.to_dict()) > 0

def test_get_trunk_datablocks(story):
    blocks = get_trunk_datablocks(story)
    assert len(blocks) > 0
    assert blocks[0].origin == Origin.root

def test_assemble_story(story, full_text):
    assert len(full_text) > 0
    assert full_text == assemble_story_datablocks(story) == assemble_story_fragments(story.fragments)


def _test_position_to_fragment(fragments, full_text, position):
    assert len(fragments) > 0
    
    if position < 0:
        with pytest.raises(ValueError):
            position_to_fragment(fragments, position)
    else:
        (fragment_number, relative_position) = position_to_fragment(fragments, position)
        
        if position >= len(full_text):
            assert (fragment_number, relative_position) == (-1,0)
        else:
            assert fragment_number >= 0
            fragment_text = fragments[fragment_number].data
            assert len(fragment_text) > 0
            assert 0 <= relative_position < len(fragment_text)
            assert full_text[position:].startswith(fragments[fragment_number].data[relative_position:])

def test_position_to_fragment(fragments, full_text):
    _test_position_to_fragment(fragments, full_text, -1)
    _test_position_to_fragment(fragments, full_text, 0)
    _test_position_to_fragment(fragments, full_text, len(full_text)-1)
    _test_position_to_fragment(fragments, full_text, len(full_text))
    _test_position_to_fragment(fragments, full_text, len(full_text)+1)
    _test_position_to_fragment(fragments, full_text, len(full_text)+10)
    _test_position_to_fragment(fragments, full_text, len(full_text)//2)

def test_position_to_empty_fragments():
    empty_fragment = Fragment(data="", origin=Origin.prompt)
    test_position_to_fragment([empty_fragment], "")
    test_position_to_fragment([empty_fragment,empty_fragment,empty_fragment], "")

@given(integers(min_value=0, max_value=40))
def test_position_around_delimiters(fragments, full_text, fragment_delimiters, i):
    assume(i < len(fragment_delimiters))
    position = fragment_delimiters[i]
    _test_position_to_fragment(fragments, full_text, position-1)
    _test_position_to_fragment(fragments, full_text, position)
    _test_position_to_fragment(fragments, full_text, position+1)
