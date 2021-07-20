import curses

from typing import List,Tuple

from .story_model import *
from .story import *

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
        self.fragment_heights: List[int] = get_fragment_heights(self.story)
        self.max_line: int = self.fragment_heights[-1]+1
        self.cursor_line: int = self.max_line
        self.cursor_position_in_line: int = max(0, len(self.story.fragments[-1].data.split("\n")[-1])-1)
        self.displayable_fragments: List["Fragment"] = [] # initialize once we have a screen!
    
    def run(self, stdscr):
        self.stdscr = stdscr
        self.init_colors()
        self.displayable_fragments = self.get_displayable_fragments(stdscr.getmaxyx()[0])
        self.display_on_screen()
        
        while True:
            c = stdscr.getch()
            
            if c == ord("q"):
                break
    
    def init_colors(self):
        curses.start_color()
        curses.use_default_colors()
        
        curses.init_pair(origin_colors[Origin.root], curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(origin_colors[Origin.ai], curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(origin_colors[Origin.prompt], curses.COLOR_YELLOW, -1)
        curses.init_pair(origin_colors[Origin.edit], curses.COLOR_MAGENTA, -1)
        curses.init_pair(origin_colors[Origin.user], curses.COLOR_CYAN, -1)
        self.stdscr.bkgd("\0", curses.color_pair(origin_colors[Origin.root]))
    
    def get_displayable_fragments(self, height: int) -> List["Fragment"]:
        self.start_fragment_number: int = max(0, line_to_fragment(self.story, self.cursor_line-height)[0])
        self.end_fragment_number: int = line_to_fragment(self.story, self.cursor_line+height)[0]
        
        return self.story.fragments[self.start_fragment_number:self.end_fragment_number]
    
    def display_on_screen(self) -> None:
        height, width = self.stdscr.getmaxyx()
        fragment_number, relative_position = line_to_fragment(self.story, self.cursor_line)
        
        if not self.start_fragment_number <= fragment_number <= self.end_fragment_number:
            # update fragment cache
            self.displayable_fragments = self.get_displayable_fragments(height)
        
        # figure out which of the cached fragments do we really need
        fragment_number -= self.start_fragment_number
        first_screen_fragment = last_screen_fragment = fragment_number
        ypos = height-1
        xpos = width-1
        self.stdscr.clear()
        #self.stdscr.move(ypos,xpos)
        
        for fragment in reversed(self.displayable_fragments[:last_screen_fragment]):
            fragment_line_count: int = 0
            
            for line in reversed(fragment.data.split("\n")):
                if fragment_line_count > 0: ypos -= 1
                if ypos < 0: break
                fragment_line_count += 1
                xpos -= len(line)
                
                if xpos < 0:
                    ypos += xpos//width
                    xpos = xpos%width
                
                if ypos < 0: break
                #print(ypos, xpos, line)
                self.stdscr.addstr(ypos, xpos, line, curses.color_pair(origin_colors[fragment.origin]))
            
            if ypos < 0:
                break
        
        self.stdscr.move(height-1, width-1)
    
    def move_cursor_right(self, by=1) -> None:
        pass
    
    def move_cursor_left(self, by=1) -> None:
        pass
    
    def move_cursor_down(self, by=1) -> None:
        pass

    def move_cursor_up(self, by=1) -> None:
        pass

    def benchmark(self, n=1000) -> float:
        from timeit import timeit
        pass


def launch_editor(story: "Story") -> None:
    editor = StoryEditor(story)
    curses.wrapper(editor.run)