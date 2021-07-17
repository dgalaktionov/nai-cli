from itertools import accumulate

from prompt_toolkit.layout import UIControl, UIContent
from prompt_toolkit.formatted_text import (
    AnyFormattedText,
    StyleAndTextTuples,
    to_formatted_text,
)

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
        newlines_per_fragment = list([f.data.count("\n") for f in self.story.fragments])
        startlines_fragment = list(accumulate(newlines_per_fragment, initial=0))
        
        def get_line(i: int) -> StyleAndTextTuples:
            fragment_number = max(next((number for number,lines in enumerate(startlines_fragment) if lines >= i))-1, 0)
            fragment = self.story.fragments[fragment_number]
            start_line = startlines_fragment[fragment_number]
            fragment_lines = fragment.data.split("\n")
            fl_position = i-start_line
            line_fragments = [("", fragment_lines[fl_position])]
            
            while fl_position == len(fragment_lines)-1 and fragment_number < len(self.story.fragments)-1:
                fl_position = 0
                fragment_number += 1
                fragment = self.story.fragments[fragment_number]
                fragment_lines = fragment.data.split("\n")
                line_fragments.append(("", fragment_lines[fl_position]))
            
            return line_fragments
        
        return UIContent(
            get_line=get_line,
            line_count=startlines_fragment[-1]+1
        )

    def benchmark(self, n=1000) -> float:
        from timeit import timeit
        content: "UIContent" = self.create_content(0,0)
        return timeit(lambda: [content.get_line(i) for i in range(content.line_count)], number=n)