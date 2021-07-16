import pytest

from naicli.story_model import *
from naicli.story import *

from hypothesis import given, assume, settings
from hypothesis.strategies import integers, text

from copy import deepcopy

@pytest.fixture(scope="module")
def book():
    return open_story_file("example/grug.story")

@pytest.fixture(scope="module")
def full_text(book):
    return assemble_story_fragments(book.content.story.fragments)

@pytest.fixture(scope="module")
def story(book):
    return book.content.story

@pytest.fixture
def empty_story():
    return Story(fragments=[], datablocks=[], step=0, currentBlock=0, version=0)

@pytest.fixture
def empty_datablock():
    return Datablock(chain=False, dataFragment=Fragment(data="", origin=Origin.edit), startIndex=0, endIndex=0, 
        fragmentIndex=-1, nextBlock=[], origin=Origin.edit, removedFragments=[], prevBlock = -1)

def test_book(book):
    assert isinstance(book, Book)
    assert len(book.to_dict()) > 0

def test_get_trunk_datablocks(story):
    blocks = get_trunk_datablocks(story)
    first_block = next(blocks)
    assert first_block.origin == Origin.root

def test_assemble_story(story, full_text):
    assert len(full_text) > 0
    assert len(story.fragments) > 0
    
    i = 0
    for fragment in story.fragments:
        assert fragment.data == full_text[i:i+len(fragment.data)]
        i += len(fragment.data)

def test_get_fragment_delimiters(story):
    fragments = story.fragments
    assert len(fragments) > 0
    
    # evaluaute two times to fully test cache
    for _ in range(2):
        end = 0
        fragment_delimiters = get_fragment_delimiters(story)
        assert len(fragments) == len(fragment_delimiters)
    
        for fragment_end, fragment in zip(fragment_delimiters, fragments):
            end += len(fragment.data)
            assert fragment_end == end

def _test_position_to_fragment(story, full_text, position):
    fragments = story.fragments
    assert len(fragments) > 0
    
    if position < 0:
        with pytest.raises(ValueError):
            position_to_fragment(story, position)
    else:
        (fragment_number, relative_position) = position_to_fragment(story, position)
        
        if position >= len(full_text):
            assert (fragment_number, relative_position) == (len(fragments),0)
        else:
            assert fragment_number >= 0
            fragment_text = fragments[fragment_number].data
            assert len(fragment_text) > 0
            assert 0 <= relative_position < len(fragment_text)
            assert full_text[position:].startswith(fragments[fragment_number].data[relative_position:])

def test_position_to_fragment(story, full_text):
    _test_position_to_fragment(story, full_text, 0)
    _test_position_to_fragment(story, full_text, len(full_text)-1)
    _test_position_to_fragment(story, full_text, len(full_text))
    _test_position_to_fragment(story, full_text, len(full_text)+1)
    _test_position_to_fragment(story, full_text, len(full_text)+10)
    _test_position_to_fragment(story, full_text, len(full_text)//2)

def test_position_to_empty_fragments(empty_story):
    empty_fragment = Fragment(data="", origin=Origin.prompt)
    empty_story.fragments = [empty_fragment]
    test_position_to_fragment(empty_story, "")
    empty_story.fragments = [empty_fragment,empty_fragment,empty_fragment]
    get_fragment_delimiters.cache_clear()
    test_position_to_fragment(empty_story, "")

@given(integers(min_value=0, max_value=40))
def test_position_around_delimiters(story, full_text, i):
    fragment_delimiters = get_fragment_delimiters(story)
    assume(i < len(fragment_delimiters))
    position = fragment_delimiters[i]
    _test_position_to_fragment(story, full_text, position-1)
    _test_position_to_fragment(story, full_text, position)
    _test_position_to_fragment(story, full_text, position+1)


def test_fragment_to_position(story):
    fragment_delimiters = get_fragment_delimiters(story)
    fragments = story.fragments
    
    # special cases first
    assert fragment_to_position(story, len(fragments)) == fragment_delimiters[-1]
    assert fragment_to_position(story, len(fragments)+1) == fragment_delimiters[-1]
    
    for fragment_number in range(len(fragment_delimiters)):
        i = fragment_number
        while i < len(fragments) and len(fragments[i].data) == 0: i += 1
        if i >= len(fragments): i == -1
        
        absolute_position: int = fragment_to_position(story, fragment_number)
        assert position_to_fragment(story, absolute_position) == (i, 0)

def test_assemble_story_datablocks(story, empty_story, full_text):
    empty_story.datablocks = story.datablocks
    empty_story.currentBlock = story.currentBlock
    final_story = assemble_story_datablocks(empty_story)
    text = assemble_story_fragments(final_story.fragments)
    assert text == full_text
    assert len(final_story.fragments) == len(story.fragments)
    
    for f1,f2 in zip(final_story.fragments, story.fragments):
        assert (f1.data, f1.origin) == (f2.data, f2.origin)

def test_append_datablock(story, empty_story, empty_datablock):
    alt_story = empty_story
    datablocks = deepcopy(story.datablocks)
    alt_story.datablocks = datablocks
    alt_story.currentBlock = story.currentBlock
    prev_datablock_number = alt_story.currentBlock
    
    assert prev_datablock_number > 0
    assert prev_datablock_number < len(datablocks)
    
    assert empty_datablock != datablocks[prev_datablock_number]
    append_datablock(alt_story, empty_datablock)
    assert alt_story.currentBlock > prev_datablock_number
    assert empty_datablock == datablocks[alt_story.currentBlock]
    assert empty_datablock.prevBlock == prev_datablock_number
    assert alt_story.currentBlock in datablocks[prev_datablock_number].nextBlock

def _i1k():
    return integers(min_value=0, max_value=1000)

@pytest.fixture(scope="module")
def story_copy(story):
    return deepcopy(story)

@given(text(), _i1k(), _i1k())
@settings(max_examples=1000)
def test_insert_text(story_copy, new_text, start_position, end_position):
    assume(end_position >= start_position)
    story_text = assemble_story_fragments(story_copy.fragments)
    new_story_text = assemble_story_fragments(insert_text(story_copy, new_text, start_position, end_position).fragments)
    assert join_strings(story_text[:start_position], new_text, story_text [end_position:]) == new_story_text
