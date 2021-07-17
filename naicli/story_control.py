from typing import List, Tuple
from itertools import accumulate
from functools import reduce, lru_cache, partial
from operator import ge

from prompt_toolkit.layout import UIControl, UIContent
from prompt_toolkit.formatted_text import (
    AnyFormattedText,
    StyleAndTextTuples,
    to_formatted_text,
)
from prompt_toolkit.formatted_text.base import OneStyleAndTextTuple

from .story_model import *
from .story import *

class StoryControl(UIControl):
    def __init__(
        self,
        story: "Story",
    ):
        self.story = story

    def is_focusable(self) -> bool:
        return True
    
    def get_key_bindings(self) -> Optional["KeyBindingsBase"]:
        return None
    
    def create_content(self, width: int, height: int) -> "UIContent":
        fragment_heights: List[int] = get_fragment_heights(self.story)
        
        @lru_cache(maxsize=1)
        def _split_text(text: str) -> List[str]:
            return text.split("\n")
        
        def _get_tuple_from_fragment(fragment_number: int, relative_line: int) -> Tuple[OneStyleAndTextTuple, bool]:
            fragment_newlines: int = fragment_heights[fragment_number+1] - fragment_heights[fragment_number]
            could_be_more: bool = relative_line == fragment_newlines and fragment_number < len(self.story.fragments)-1
            fragment: "Fragment" = self.story.fragments[fragment_number]
            
            if fragment_newlines > 0:
                return (("", _split_text(fragment.data)[relative_line]), could_be_more)
            else:
                return (("", fragment.data), could_be_more)
        
        def get_line(i: int) -> StyleAndTextTuples:
            fragment_number, relative_line = position_to_fragment(self.story, i, get_fragment_heights, comparator=ge)
            line_fragments: StyleAndTextTuples = []
            could_be_more: bool = True
            
            while could_be_more:
                line_fragment, could_be_more = _get_tuple_from_fragment(fragment_number, relative_line)
                line_fragments.append(line_fragment)
                fragment_number += 1
                relative_line = 0
            
            return line_fragments
        
        return UIContent(
            get_line=get_line,
            line_count=fragment_heights[-1]+1
        )

    def benchmark(self, n=1000) -> float:
        from timeit import timeit
        content: "UIContent" = self.create_content(0,0)
        return timeit(lambda: [content.get_line(i) for i in range(content.line_count)], number=n)