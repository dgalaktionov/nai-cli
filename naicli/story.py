import json
from typing import List, Iterator
from functools import reduce, lru_cache, partial
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

@lru_cache(maxsize=1)
def get_fragment_delimiters(story: "Story") -> List[int]:
    """
        Given a Story with Fragments, returns a list with the end position that each fragment would correspond to in 
        the final text, effectively providing the delimiting positions that separate the fragments.
        Cached for efficiency, must remember to invalidate when fragments are added or removed!
        
        TODO: consider indexing in a nice tree for better update times.
    """
    return list(accumulate(map(lambda f: len(f.data), story.fragments)))

def position_to_fragment(story: "Story", absolute_position: int) -> (int, int):
    """
        Given a position in the final text, return a pair of (fragment_number, relative_position), 
        the first element being the number of the fragment that would contain that final position, 
        while the second element is the equivalent relative position inside the mentioned fragment.
        When the position is at the end of the final text, (-1,0) is returned.
        
        TODO: consider implementing an exponential search for faster lookup
    """
    if absolute_position < 0:
        raise ValueError(f"Supplied a negative absolute position {absolute_position}")
    
    fragment_delimiters = enumerate(get_fragment_delimiters(story))
    return next(((i, absolute_position - frag_end + len(story.fragments[i].data)) 
        for i, frag_end in fragment_delimiters if frag_end > absolute_position), (-1, 0))

def insert_text(story: "Story", text: str, pos: int) -> "Story":
    #probably should be insert_fragment instead, or even change apply_datablock to make more sense...
    pass