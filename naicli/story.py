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
        block: "Datablock" = story.datablocks[blockPos]
        blocks.append(block)
        blockPos = block.prevBlock
        
    return reversed(blocks)

def assemble_story_datablocks(story: "Story") -> "Story":
    return reduce(apply_datablock, get_trunk_datablocks(story), story)
    
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
        When the position is at the end of the final text, (len(story.fragments),0) is returned.
    """
    if absolute_position < 0:
        raise ValueError(f"Supplied a negative absolute position {absolute_position}")
    
    fragment_delimiters: List[int] = get_fragment_delimiters(story)
    
    """
        In practice, most of the displaying and editing will be performed close to the end of the text.
        This simple heuristic allows me to determine if the exponential search should start from the end (rightmost) 
        fragments instead of the start (leftmost) ones.
    """
    search_from_end: bool = len(fragment_delimiters) > 0 and absolute_position >= fragment_delimiters[len(fragment_delimiters)//2]
    fragment_number: int = exponential_search(fragment_delimiters, absolute_position, from_end=search_from_end)
    fragment_start: int = 0 if fragment_number == 0 else fragment_delimiters[fragment_number-1]
    relative_position: int = 0 if fragment_number >= len(fragment_delimiters) else absolute_position - fragment_start
    return (fragment_number, relative_position)

def fragment_to_position(story: "Story", fragment_number: int) -> int:
    """
        For a fragment number, returns the starting position in the final text.
    """
    fragment_delimiters: List[int] = get_fragment_delimiters(story)
    
    if fragment_number >= len(fragment_delimiters):
        # for consistency with position_to_fragment
        return fragment_delimiters[-1]
    
    return fragment_delimiters[fragment_number] - len(story.fragments[fragment_number].data)

def apply_datablock(story: "Story", block: "Datablock") -> "Story":
    """ 
        Apply the given editing Datablock to accordingly alter the Story fragments.
        
        Sometimes, like for blocks with origin "user", block.startId <= block.endId can be false.
        Since NAI does not seem to ever generate blocks with the intentions of copying from past text, 
        I choose to interpret it the same way as if endIndex held the same value as startIndex, 
        i.e a text insertion case.
    """
    start_fragment_number, start_relative_position = position_to_fragment(story, block.startIndex)
    fragments: List["Fragment"] = story.fragments
    
    if start_fragment_number >= len(fragments):
        # append
        block.fragmentIndex = start_fragment_number if len(fragments) > 0 else -1
        fragments.append(block.dataFragment)
    else:
        # insert before the end
        end_fragment_number, end_relative_position = position_to_fragment(story, block.endIndex)
        
        if end_fragment_number >= len(fragments):
            # the last fragment must always survive!
            end_fragment_number, end_relative_position = len(fragments)-1, len(fragments[-1].data)
        
        start_fragment, end_fragment = fragments[start_fragment_number], fragments[end_fragment_number]
        new_start_fragment = Fragment(data=start_fragment.data[:start_relative_position], origin=start_fragment.origin)
        new_end_fragment = Fragment(data=end_fragment.data[end_relative_position:], origin=end_fragment.origin)
        
        # i hate to do it the mutable way, but it is simply more efficient
        if start_fragment == end_fragment: end_relative_position -= start_relative_position
        start_fragment.data = start_fragment.data[start_relative_position:]
        end_fragment.data = end_fragment.data[:end_relative_position]
        block.removedFragments = fragments[start_fragment_number:end_fragment_number+1]
        block.fragmentIndex = start_fragment_number+1
        fragments[start_fragment_number:end_fragment_number+1] = [new_start_fragment, block.dataFragment, new_end_fragment]
    
    get_fragment_delimiters.cache_clear()
    return story

def insert_text(story: "Story", text: str, pos: int) -> "Story":
    #probably should be insert_fragment instead, or even change apply_datablock to make more sense...
    pass