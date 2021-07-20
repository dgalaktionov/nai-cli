import json
from typing import List, Iterator, Optional, Callable, Tuple
from functools import reduce, lru_cache, partial
from itertools import accumulate
from operator import gt
from bisect import bisect_right, bisect_left

from .util import *
from .story_model import *

class FragmentInfo:
    def __init__(self, fragment: "Fragment"):
        self.fragment: "Fragment" = fragment
        self.line_lengths: List[int] = [len(line) for line in fragment.data.split("\n")]
        #self.line_positions = list(accumulate([length for length in self.line_lengths], initial=0))
        self.line_positions = list(accumulate([length+1 for length in self.line_lengths], initial=0))
        self.line_positions[-1] -= 1
        self.prev: "FragmentInfo" = None
        self.next: "FragmentInfo" = None
    
    @property
    def text_length(self) -> int:
        return len(self.fragment.data)
    
    @property
    def height(self) -> int:
        return len(self.line_lengths)-1
    
    def line_to_pos(self, line: int=0) -> int:
        return self.line_positions[line]
    
    def pos_to_line(self, pos: int=0) -> Tuple[int,int]:
        line_number = max(0, next((i for i,l in enumerate(self.line_positions) if l > pos), len(self.line_lengths))-1)
        return (line_number, pos - self.line_to_pos(line_number)) 

@lru_cache(maxsize=None)
def get_fragment_info(fragment: "Fragment") -> "FragmentInfo":
    return FragmentInfo(fragment)

def get_fragment_infos(fragments: List["FragmentInfo"]) -> List["FragmentInfo"]:
    fragment_infos: List["FragmentInfo"] = [get_fragment_info(f) for f in fragments]
    prev: "FragmentInfo" = None if len(fragment_infos) == 0 else fragment_infos[0]

    if prev != None and prev.next == None:
        # no linked structure, must populate!
        for fi in fragment_infos[1:]:
            prev.next = fi
            fi.prev = prev
            prev = fi
    
    return fragment_infos

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
    return list(accumulate([fi.text_length for fi in get_fragment_infos(story.fragments)], initial=0))

@lru_cache(maxsize=1)
def get_fragment_heights(story: "Story") -> List[int]:
    """
        Given a Story with Fragments, returns a list with the starting number of the line that 
        each fragment would correspond to in the final text. Like with get_fragment_delimiters, 
        the last value indicates the total number of lines in the text.
        Cached for efficiency, must remember to invalidate when fragments are added or removed!
        
        TODO: consider indexing in a nice tree for better update times.
    """
    return list(accumulate([fi.height for fi in get_fragment_infos(story.fragments)], initial=0))

def invalidate_caches():
    get_fragment_delimiters.cache_clear()
    get_fragment_heights.cache_clear()

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
        get_fragment_infos(fragments[-2:])
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
        block.removedFragments = fragments[start_fragment_number:end_fragment_number+1]
        block.fragmentIndex = start_fragment_number+1
        inserted_fragments = [new_start_fragment, block.dataFragment, new_end_fragment]
        fragments[start_fragment_number:end_fragment_number+1] = inserted_fragments
        
        # update linked list structures
        start_info, end_info = get_fragment_info(start_fragment), get_fragment_info(end_fragment)
        [new_start_info,_,new_end_info] = get_fragment_infos(inserted_fragments)
        new_start_info.prev = start_info.prev
        new_end_info.next = end_info.next
        if new_start_info.prev: start_info.prev.next = new_start_info
        if new_end_info.next: end_info.next.prev = new_end_info
    
    invalidate_caches()
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