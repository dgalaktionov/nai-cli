import json
from typing import List, Iterator, Optional, Callable
from functools import reduce, lru_cache, partial
from itertools import accumulate
from operator import gt
from bisect import bisect_right, bisect_left

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
        Given a Story with n Fragments, returns a list of n+1 with the starting positions that each fragment would have in 
        the final text, effectively providing the delimiting positions that separate the fragments. The last value indicates 
        the total length of the text.
        Cached for efficiency, must remember to invalidate when fragments are added or removed!
        
        TODO: consider indexing in a nice tree for better update times.
    """
    return list(accumulate([len(f.data) for f in story.fragments], initial=0))

@lru_cache(maxsize=1)
def get_fragment_heights(story: "Story") -> List[int]:
    """
        Given a Story with Fragments, returns a list with the starting number of the line that 
        each fragment would correspond to in the final text. Like with get_fragment_delimiters, 
        the last value indicates the total number of lines in the text.
        Cached for efficiency, must remember to invalidate when fragments are added or removed!
        
        TODO: consider indexing in a nice tree for better update times.
    """
    return list(accumulate([f.data.count("\n") for f in story.fragments], initial=0))

def position_to_fragment(story: "Story", absolute_position: int, 
    get_data: Callable[["Story"], List[int]] = get_fragment_delimiters, search_method=bisect_right) -> (int, int):
    """
        Given a position in the final text, return a pair of (fragment_number, relative_position), 
        the first element being the number of the fragment that would contain that final position, 
        while the second element is the equivalent relative position inside the mentioned fragment.
        When the position is at the end of the final text, (len(story.fragments),0) is returned.
        
        By default it works over the position index. If, for example, one would like to return the 
        fragment number for an absolute text height, then get_fragment_heights should be passed in get_data.
    """
    fragment_delimiters: List[int] = get_data(story)
    #search_from_end: bool = len(fragment_delimiters) > 0 and absolute_position >= fragment_delimiters[len(fragment_delimiters)//2]
    fragment_number: int = 0
    #fragment_number = max(0, exponential_search(fragment_delimiters, absolute_position, comparator=comparator, from_end=search_from_end)-1)
    fragment_number = max(0, search_method(fragment_delimiters, absolute_position)-1)
    fragment_start: int = fragment_delimiters[fragment_number]
    relative_position: int = 0 if fragment_number >= len(story.fragments) else absolute_position - fragment_start
    return (fragment_number, relative_position)

def line_to_fragment(story: "Story", absolute_position: int) -> (int, int):
    return position_to_fragment(story, absolute_position, get_data=get_fragment_heights, search_method=bisect_left)

def fragment_to_position(story: "Story", fragment_number: int, get_data: Callable[["Story"], List[int]] = get_fragment_delimiters) -> int:
    """
        For a fragment number, returns the starting position in the final text.
        
        By default it works over the position index. If, for example, one would like to return the 
        height of a fragment, then get_fragment_heights should be passed in get_data.
    """
    fragment_delimiters: List[int] = get_data(story)
    
    if fragment_number >= len(story.fragments):
        # for consistency with position_to_fragment
        return fragment_delimiters[-1]
    
    return fragment_delimiters[fragment_number]

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
    get_fragment_heights.cache_clear()
    return story

def append_datablock(story: "Story", block: "Datablock") -> None:
    datablocks: List["Datablock"] = story.datablocks
    datablocks.append(block)
    block_num: int = len(datablocks)-1
    block.prevBlock = story.currentBlock
    datablocks[story.currentBlock].nextBlock.append(block_num)
    story.currentBlock = block_num

def insert_text(story: "Story", text: str, start_position: int, end_position: Optional[int] = None, origin: "Origin" = Origin.edit) -> "Story":
    if not end_position or end_position < start_position: end_position = start_position
    block: "Datablock" = Datablock(chain=False, dataFragment=Fragment(data=text, origin=origin), startIndex=start_position, endIndex=end_position, 
        fragmentIndex=-1, nextBlock=[], origin=origin, removedFragments=[], prevBlock=-1)
    apply_datablock(story, block)
    append_datablock(story, block)
    return story