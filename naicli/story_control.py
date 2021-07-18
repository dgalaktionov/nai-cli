from typing import List, Tuple, Iterable
from itertools import accumulate
from functools import reduce, lru_cache, partial
from operator import ge

from prompt_toolkit.data_structures import Point
from prompt_toolkit.layout import UIControl, UIContent
from prompt_toolkit.formatted_text import (
    AnyFormattedText,
    StyleAndTextTuples,
    to_formatted_text,
)
from prompt_toolkit.formatted_text.base import OneStyleAndTextTuple
from prompt_toolkit.key_binding.key_bindings import KeyBindingsBase
from prompt_toolkit.utils import Event

from .story_model import *
from .story import *
from .util import *

colors = {
    Origin.root: "",
    Origin.prompt: "#ffcc00",
    Origin.ai: "",
    Origin.edit: "#ff5566",
    Origin.user: "#66ffff"
}


class StoryControl(UIControl):
    def __init__(
        self,
        story: "Story",
    ):
        self.story = story
        
        # deprecated for now
        self.cursor_fragment_number = -1
        self.cursor_relative_position = -1
        
        self.cursor_position = Point(0,1)

    def is_focusable(self) -> bool:
        return True
    
    def get_key_bindings(self) -> Optional["KeyBindingsBase"]:
        return None
    
    def create_content(self, width: int, height: int) -> "UIContent":
        fragment_heights: List[int] = get_fragment_heights(self.story)
        
        @lru_cache(maxsize=100)
        def _split_text(text: str) -> List[str]:
            return text.split("\n")
        
        def _get_cursor_position_legacy() -> Point:
            start_line: int = fragment_heights[self.cursor_fragment_number]
            fragment_newlines: int = fragment_heights[self.cursor_fragment_number+1] - start_line
            start_line_fragment_number, relative_line = line_to_fragment(self.story, start_line)
            x,y = 0,start_line
            
            if fragment_newlines > 0:
                # the current fragment has several lines, figure out which has the cursor
                y += self.story.fragments[self.cursor_fragment_number].data[:self.cursor_relative_position].count("\n")
            
            relative_line_start = 0
            
            if relative_line > 0:
                relative_line_start = find_nth(self.story.fragments[start_line_fragment_number].data, "\n", relative_line-1)
            
            x = self.cursor_relative_position - relative_line_start
            
            if start_line_fragment_number < self.cursor_fragment_number:
                x += fragment_to_position(self.story, self.cursor_fragment_number) - fragment_to_position(self.story, start_line_fragment_number)
            
            print(x,y)
            return Point(x,y)
        
        def _get_tuple_from_fragment(fragment_number: int, relative_line: int) -> Tuple[OneStyleAndTextTuple, bool]:
            fragment_newlines: int = fragment_heights[fragment_number+1] - fragment_heights[fragment_number]
            could_be_more: bool = relative_line == fragment_newlines and fragment_number < len(self.story.fragments)-1
            fragment: "Fragment" = self.story.fragments[fragment_number]
            fragment_color = colors[fragment.origin]
            
            if fragment_newlines > 0:
                return ((fragment_color, _split_text(fragment.data)[relative_line]), could_be_more)
            else:
                return ((fragment_color, fragment.data), could_be_more)
        
        def get_line(i: int) -> StyleAndTextTuples:
            fragment_number, relative_line = line_to_fragment(self.story, i)
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
            line_count=fragment_heights[-1]+1,
            cursor_position=self.cursor_position
        )
    
    def move_cursor_down(self) -> None:
        x,y = self.cursor_position
        y = max(get_fragment_heights(self.story), y+1)
        self.cursor_position = Point(x,y+1)

    def move_cursor_up(self) -> None:
        x,y = self.cursor_position
        y = min(0,y-1)
        self.cursor_position = Point(x,y-1)

    def benchmark(self, n=1000) -> float:
        from timeit import timeit
        content: "UIContent" = self.create_content(0,0)
        return timeit(lambda: [content.get_line(i) for i in range(content.line_count)], number=n)
    
    def get_invalidate_events(self) -> Iterable["Event[object]"]:
        #yield self.on_text_changed
        #yield self.on_cursor_position_changed
        return []