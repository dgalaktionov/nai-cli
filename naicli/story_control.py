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
        full_text: str = assemble_story_fragments(self.story.fragments)
        lines_per_fragment = list(accumulate([f.data.count("\n") for f in self.story.fragments]))
        
        def get_line(i: int) -> StyleAndTextTuples:
            fragment_number = next((number for number,lines in enumerate(lines_per_fragment) if lines > i))
            fragment = self.story.fragments[fragment_number]
            start_lines = 0 if fragment_number == 0 else lines_per_fragment[fragment_number-1]
            return [("", fragment.data.split("\n")[i-start_lines])]
        
        return UIContent(
            get_line=get_line,
            line_count=lines_per_fragment[-1]
        )
