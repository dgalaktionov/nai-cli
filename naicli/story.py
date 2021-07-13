import json
from typing import List, Iterator

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
    """ Sometimes, like for blocks with origin "user", block.startId <= block.endId can be false.
        Since NAI does not seem to ever generate blocks with the intentions of copying from past text, 
        I choose to interpret it the same way as if endIndex held the same value as startIndex, 
        i.e a text insertion case.
    """
    return "".join((text[:block.startIndex], block.dataFragment.data, text[max(block.startIndex, block.endIndex):]))

def assemble_story_datablocks(story: "Story") -> str:
    blocks = get_trunk_datablocks(story)
    text = ""
    
    for block in blocks:
        text = apply_datablock(text, block)
        #print(text)
        #print("")
    
    return text
    
def assemble_story_fragments(story: "Story") -> str:
    return "".join([f.data for f in story.fragments])

