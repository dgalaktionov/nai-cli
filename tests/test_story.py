import pytest

from naicli.story_model import *
from naicli.story import *

@pytest.fixture(scope="module")
def book():
    return open_story_file("example/grug.story")


def test_book(book):
    assert isinstance(book, Book)
    assert len(book.to_dict()) > 0

def test_get_trunk_datablocks(book):
    blocks = get_trunk_datablocks(book.content.story)
    assert len(blocks) > 0
    assert blocks[0].origin == Origin.root

def test_assemble_story(book):
    assert assemble_story_datablocks(book.content.story) == assemble_story_fragments(book.content.story)

