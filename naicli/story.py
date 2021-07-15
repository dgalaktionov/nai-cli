import json
from typing import List, Iterator
from functools import reduce
from itertools import accumulate

from .util import *
from .story_model import *

def open_story_file(path: str) -> "Book":
    sf = open(path, "r", encoding="utf-8")
    book = Bookfromdict(json.load(sf))
    sf.close()
    
    return book

def get_trunk_datablocks(story: "Story") -> List["Datablock"]:
    blockPos: int = story.currentBlock
    blocks: List["Datablock"] = []
    
    while blockPos >= 0:
        block = story.datablocks[blockPos]
        blocks.append(block)
        blockPos = block.prevBlock
        
    return list(reversed(blocks))

def apply_datablock(text: str, block: "Datablock") -> str:
    """ 
        Sometimes, like for blocks with origin "user", block.startId <= block.endId can be false.
        Since NAI does not seem to ever generate blocks with the intentions of copying from past text, 
        I choose to interpret it the same way as if endIndex held the same value as startIndex, 
        i.e a text insertion case.
    """
    return join_strings(text[:block.startIndex], block.dataFragment.data, text[max(block.startIndex, block.endIndex):])

def assemble_story_datablocks(story: "Story") -> str:
    return reduce(apply_datablock, get_trunk_datablocks(story), "")
    
def assemble_story_fragments(fragments: List["Fragment"]) -> str:
    return join_strings(*[f.data for f in fragments])

def position_to_fragment(fragments: List["Fragment"], absolute_position: int) -> (int, int):
    """
        Given a position in the final text, return a pair of (fragment_number, relative_position), 
        the first element being the number of the fragment that would contain that final position, 
        while the second element is the equivalent relative position inside the mentioned fragment.
        When the position is at the end of the final text, (-1,0) is returned.
        
        TODO: consider building a nice tree to index this for faster lookup
    """
    if absolute_position < 0:
        raise ValueError(f"Supplied a negative absolute position {absolute_position}")
    
    fragment_ends = enumerate(accumulate(map(lambda f: len(f.data), fragments)))
    return next(((fragment_number, absolute_position - fragment_end + len(fragments[fragment_number].data)) 
        for fragment_number, fragment_end in fragment_ends if fragment_end > absolute_position), (-1, 0))

def insert_text(story: "Story", text: str, pos: int) -> "Story":
    #probably should be insert_fragment instead, or even change apply_datablock to make more sense...
    pass