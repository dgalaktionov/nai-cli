import curses

from typing import List,Tuple

from .story_model import *
from .story import *
from .util import *

origin_colors = {
    Origin.root: 1,
    Origin.ai: 1,
    Origin.prompt: 2,
    Origin.edit: 3,
    Origin.user: 4,
}

class StoryEditor():
    def __init__(
        self,
        story: "Story",
    ):
        self.story: "Story" = story
        self.cursor_fragment: int = len(story.fragments)
        self.cursor_line_in_fragment: int = 0
        self.cursor_position_in_line: int = 0
    
    def run(self, stdscr):
        self.stdscr = stdscr
        self.init_colors()
        get_fragment_infos(self.story.fragments)
        self.display_on_screen(self.get_top_screen_fragment())
        
        while True:
            c = stdscr.getch()
            
            if c == ord("q"):
                break
        
        #print(self.benchmark())
    
    def init_colors(self):
        curses.start_color()
        curses.use_default_colors()
        
        curses.init_pair(origin_colors[Origin.root], curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(origin_colors[Origin.ai], curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(origin_colors[Origin.prompt], curses.COLOR_YELLOW, -1)
        curses.init_pair(origin_colors[Origin.edit], curses.COLOR_MAGENTA, -1)
        curses.init_pair(origin_colors[Origin.user], curses.COLOR_CYAN, -1)
        self.stdscr.bkgd("\0", curses.color_pair(origin_colors[Origin.root]) | curses.A_BOLD)
    
    def get_top_screen_fragment(self) -> Tuple[int, int, int]:
        height, width = self.stdscr.getmaxyx()
        last_screen_fragment: int = self.cursor_fragment
        first_screen_fragment: int = min(last_screen_fragment, len(self.story.fragments)-1)
        ypos: int = height-1 # we're always assuming ypos is at the end for now
        xpos: int = width-1
        
        first_fragment_line: int = 0
        first_line_position: int = 0
        
        fragment_info: "FragmentInfo" = get_fragment_info(self.story.fragments[first_screen_fragment])
        
        while fragment_info and ypos >= 0:
            first_fragment_line: int = fragment_info.height
            
            for line, length in reversed(list(enumerate(fragment_info.line_lengths))):
                if first_screen_fragment == last_screen_fragment and line > self.cursor_line_in_fragment: continue
                
                if line < fragment_info.height: 
                    ypos -= 1
                    xpos = width-1
                
                if ypos < 0: break
                first_fragment_line = line
                xpos -= length
                
                if xpos < 0:
                    ypos += xpos//width
                    xpos = xpos%width
                
                if ypos < 0: 
                    first_line_position = -ypos*width
                    break
            
            fragment_info = fragment_info.prev
            
            if fragment_info and ypos >= 0:
                first_screen_fragment -= 1
        
        return (first_screen_fragment, first_fragment_line, first_line_position)
    
    def get_remaining_screen_space(self) -> int:
        height, width = self.stdscr.getmaxyx()
        y, x = self.stdscr.getyx()
        return width*(height-y) - x - 1
    
    def display_fragment(self, fragment_info: "FragmentInfo", start_at: int = 0) -> bool:
        fragment: "Fragment" = fragment_info.fragment
        attr: int = curses.color_pair(origin_colors[fragment.origin]) | curses.A_BOLD
        text: str = fragment.data if start_at == 0 else fragment.data[start_at:]
    
        if fragment_info.height > 0:
            for line_number, line in enumerate(split_lines(text)):
                if line_number > 0:
                    if self.stdscr.getyx()[0] >= self.stdscr.getmaxyx()[0]-1:
                        # we need a newline but we ran out of vertical space!
                        return False
                    
                    self.stdscr.addch("\n")
                
                self.stdscr.addnstr(line, self.get_remaining_screen_space(), attr)
                
                
        else:
            self.stdscr.addnstr(text, self.get_remaining_screen_space(), attr)
        
        return self.get_remaining_screen_space() > 0
    
    def display_on_screen(self, start_at: Tuple[int, int, int] = (0,0,0)) -> None:
        first_screen_fragment, first_fragment_line, first_line_position = start_at
        fragment_info: "FragmentInfo" = get_fragment_info(self.story.fragments[first_screen_fragment])
        self.stdscr.clear()
        self.stdscr.move(0,0)
        
        first_offset: int = fragment_info.line_to_pos(first_fragment_line)+first_line_position
        
        while self.display_fragment(fragment_info, first_offset) and fragment_info.next:
            first_offset = 0
            fragment_info = fragment_info.next
    
    def move_cursor_right(self, by=1) -> None:
        pass
    
    def move_cursor_left(self, by=1) -> None:
        pass
    
    def move_cursor_down(self, by=1) -> None:
        pass

    def move_cursor_up(self, by=1) -> None:
        pass

    def benchmark(self, n=10000) -> float:
        from timeit import timeit
        height = self.stdscr.getmaxyx()[0]
        #return timeit(lambda: self.get_displayable_fragments(height), number=n)
        #return timeit(lambda: self.display_on_screen(), number=n)/n
        return timeit(lambda: self.display_on_screen(self.get_top_screen_fragment()), number=n)/n


def launch_editor(story: "Story") -> None:
    editor = StoryEditor(story)
    curses.wrapper(editor.run)
