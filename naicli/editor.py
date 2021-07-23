import curses

from typing import List,Tuple,Optional,NewType

from .story_model import *
from .story import *
from .util import *

ScreenCoordinates = NewType("ScreenCoordinates", Tuple[int,int])
LineCoordinates = NewType("LineCoordinates", Tuple[int,int])
StyledChunk = NewType("StyledChunk", Tuple[str,int])
StyledLine = NewType("StyledLine", List[StyledChunk])

origin_colors = {
    Origin.root: 1,
    Origin.ai: 1,
    Origin.prompt: 2,
    Origin.edit: 3,
    Origin.user: 4,
}

class Editor():
    def __init__(
        self
    ):
        self.cursor_line: LineCoordinates = (0,0)
        self.screen_line, self.screen_line_y = 0,0
        self.running: bool = False
    
    def run(self, stdscr, listen_input: bool = True):
        self.stdscr = stdscr
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)
        stdscr.scrollok(True)
        self.init_colors()
        get_fragment_infos(self.story.fragments)
        self.display_lines()
        
        event_handlers = {
            ord("q"): self.quit,
            curses.KEY_LEFT: self.move_cursor_left,
            curses.KEY_RIGHT: self.move_cursor_right,
            curses.KEY_UP: self.move_cursor_up,
            curses.KEY_DOWN: self.move_cursor_down,
        }
        
        if listen_input:
            self.running = True
            while self.running:
                c = stdscr.getch()
                if c in event_handlers: event_handlers[c]()
    
    def quit(self):
        self.running = False
        if self.stdscr: self.stdscr.keypad(False)
        curses.nocbreak()
        curses.echo()
        curses.endwin()
    
    def init_colors(self):
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(99, curses.COLOR_WHITE, curses.COLOR_BLACK)
        self.stdscr.bkgd("\0", curses.color_pair(99) | curses.A_BOLD)
    
    def get_screen_cursor(self, destination: Optional[LineCoordinates] = None) -> ScreenCoordinates:
        if destination == None: destination = self.cursor_line
        height, width = self.stdscr.getmaxyx()
        line_number: int = self.screen_line-1
        y,x= -1,0
        
        while line_number < destination[0] and y < height:
            line_number += 1
            y += 1
            line_length: int = self.line_length(self.get_line(line_number))
            line_height: int = line_length//width
            line_pos: int = min(destination[1], line_length)
            
            if line_number == destination[0]:
                line_height = line_pos//width
                x = line_pos%width
            
            if line_number == self.screen_line: line_height -= self.screen_line_y
            y += line_height
        
        return (y,x)
    
    def get_cursor_line(self, screen_cursor_pos: Optional[ScreenCoordinates] = None) -> LineCoordinates:
        if screen_cursor_pos == None: screen_cursor_pos = self.stdscr.getyx()
        height, width = self.stdscr.getmaxyx()
        number_of_lines: int = self.get_number_of_lines()
        line_number: int = self.screen_line
        y,x = -self.screen_line_y-1,0
        line_length: int = 0
        
        while line_number < number_of_lines and y < screen_cursor_pos[0] < height:
            y += 1
            line_length = self.line_length(self.get_line(line_number))
            line_height: int = max(0,line_length-1)//width
            
            y+=line_height
            if y >= screen_cursor_pos[0]:
                pos: int = min(width*(line_height-y+screen_cursor_pos[0]) + screen_cursor_pos[1], line_length)
                return (line_number, pos)
            
            line_number += 1
        
        return (number_of_lines-1, line_length)
    
    def draw_cursor(self) -> None:
        self.stdscr.move(*self.get_screen_cursor())
    
    def displace_screen_cursor(self, by: int=0, from_pos: Optional[ScreenCoordinates] = None) -> ScreenCoordinates:
        height, width = self.stdscr.getmaxyx()
        y, x = from_pos if from_pos else self.stdscr.getyx()
        
        x += by
        
        if not 0 <= x < width:
            y += x//width
            x = x%width
        
        if y < 0:
            y,x = 0,0
        
        return (y,x)
    
    def get_line(self, line: int) -> StyledLine:
        raise NotImplemented("Override this method in your editor!")
    
    def get_number_of_lines(self) -> int:
        # TODO actually implement this
        return 1000000
    
    def line_length(self, line: StyledLine):
        return sum([len(text) for text,_ in line])
    
    def line_height(self, line: StyledLine):
        width = self.stdscr.getmaxyx()[1]
        return 1+line_length(line)//width
    
    def display_lines(self) -> None:
        height, width = self.stdscr.getmaxyx()
        ypos: int = height-1 # we're always assuming ypos is at the end for now
        xpos: int = 0
        line_number: int = self.cursor_line[0]
        
        while line_number >= 0 and ypos >= 0:
            line: StyledLine = self.get_line(line_number)
            length: int = self.line_length(line)
            ypos -= length//width
            
            if ypos < 0:
                # we've gotta trim this line to fit
                skipped_text: int = 0
                trimmed_line: StyledLine = []
                
                for text,style in line:
                    if skipped_text >= -ypos*width:
                        trimmed_line.append((text,style))
                    else:
                        skipped_text += len(text)
                        
                        if skipped_text > -ypos*width:
                            trimmed_line.append((text[len(text)-ypos*width-skipped_text:],style))
                
                self.screen_line = line_number
                self.screen_line_y = -ypos
                line = trimmed_line
                ypos = 0
            
            self.stdscr.move(ypos,xpos)
            
            for text,style in line:
                self.stdscr.addstr(text, style)
            
            ypos -= 1
            line_number -= 1
        
        if ypos >= 0:
            self.stdscr.scroll(ypos+1)
        
        self.screen_line = line_number + 1
        self.draw_cursor()
    
    def get_remaining_screen_space(self) -> int:
        height, width = self.stdscr.getmaxyx()
        y, x = self.stdscr.getyx()
        return width*(height-y) - x - 1
    
    def move_cursor_right(self, by=1) -> None:
        self.cursor_line = self.get_cursor_line(self.displace_screen_cursor(by))
        self.draw_cursor()
    
    def move_cursor_left(self, by=1) -> None:
        self.cursor_line = self.get_cursor_line(self.displace_screen_cursor(-by))
        self.draw_cursor()
    
    def move_cursor_down(self, by=1) -> None:
        y,x = self.get_screen_cursor()
        y += by
        self.cursor_line = self.get_cursor_line((y,x))
        self.draw_cursor()

    def move_cursor_up(self, by=1) -> None:
        y,x = self.get_screen_cursor()
        y = max(0, y-by)
        self.cursor_line = self.get_cursor_line((y,x))
        self.draw_cursor()


class StoryEditor(Editor):
    def __init__(
        self,
        story: "Story",
    ):
        super(StoryEditor,self).__init__()
        self.story: "Story" = story
        self.cursor_line: LineCoordinates = (fragment_to_position(story, len(story.fragments), get_data=get_fragment_heights), 0)
    
    def run(self, stdscr, listen_input: bool = True):
        super(StoryEditor,self).run(stdscr, listen_input)
        #print(self.benchmark())
    
    def init_colors(self):
        super(StoryEditor,self).init_colors()
        curses.init_pair(origin_colors[Origin.root], curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(origin_colors[Origin.ai], curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(origin_colors[Origin.prompt], curses.COLOR_YELLOW, -1)
        curses.init_pair(origin_colors[Origin.edit], curses.COLOR_MAGENTA, -1)
        curses.init_pair(origin_colors[Origin.user], curses.COLOR_CYAN, -1)
    
    def get_line(self, line: int) -> StyledLine:
        line_chunks: StyledLine = []
        fragment_number, relative_line = line_to_fragment(self.story, line)
        if fragment_number >= len(self.story.fragments): return line_chunks
        fragment_info: "FragmentInfo" = get_fragment_info(self.story.fragments[fragment_number])
        
        while fragment_info:
            position: int = fragment_info.line_to_pos(relative_line)
            length: int = fragment_info.line_lengths[relative_line]
            line_chunks.append((fragment_info.fragment.data[position:position+length], curses.color_pair(origin_colors[fragment_info.fragment.origin]) | curses.A_BOLD))
            
            if relative_line < fragment_info.height:
                # all chunks are contained in one single fragment line, ain't that nice
                break
            
            # guess we're not that lucky today, gotta keep iterating
            fragment_info = fragment_info.next
            relative_line = 0
        
        return line_chunks
    
    def get_number_of_lines(self) -> int:
        return 1+fragment_to_position(self.story, len(self.story.fragments), get_data=get_fragment_heights)
    
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
                    ypos,xpos = self.move_screen_cursor(-1, pos=(ypos,xpos))
                
                if ypos < 0: break
                first_fragment_line = line
                ypos,xpos = self.move_screen_cursor(-length, pos=(ypos,xpos))
                
                if ypos < 0: 
                    first_line_position = -ypos*width
                    break
            
            fragment_info = fragment_info.prev
            
            if fragment_info and ypos >= 0:
                first_screen_fragment -= 1
        
        return (first_screen_fragment, first_fragment_line, first_line_position)
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
    
    def display_on_screen(self, start_at: Tuple[int,int,int] = (0,0,0)) -> None:
        first_screen_fragment, first_fragment_line, first_line_position = start_at
        fragment_info: "FragmentInfo" = get_fragment_info(self.story.fragments[first_screen_fragment])
        self.stdscr.clear()
        self.stdscr.move(0,0)
        
        first_offset: int = fragment_info.line_to_pos(first_fragment_line)+first_line_position
        
        while self.display_fragment(fragment_info, first_offset) and fragment_info.next:
            first_offset = 0
            fragment_info = fragment_info.next
    
    def move_cursor_in_fragment(fragment_info: "FragmentInfo", by: int=0) -> int:
        if fragment_info.text_length == 0:
            # skip empty fragment, nothing to move!
            return by
        
        while by != 0 and 0 <= self.cursor_line_in_fragment <= fragment_index.height:
            pos: int = self.cursor_position_in_line + by
            
            if 0 <= pos < fragment_info.line_lengths[self.cursor_line_in_fragment]:
                # all within the same line!
                self.cursor_position_in_line += by
                self.stdscr.move(self.move_screen_cursor(by))
                by = 0
            elif pos < 0:
                by += self.cursor_position_in_line
                self.cursor_line_in_fragment -= 1
                self.cursor_position_in_line = fragment_info.line_lengths[self.cursor_line_in_fragment] if self.cursor_line_in_fragment >= 0 else 0
            else:
                by -= fragment_info.line_lengths[self.cursor_line_in_fragment] + self.cursor_position_in_line
                self.cursor_line_in_fragment += 1
                self.cursor_position_in_line = 0
        
        self.cursor_line_in_fragment = max(0, min(fragment_info.height, self.cursor_line_in_fragment))
        return by

    def benchmark(self, n=10000) -> float:
        from timeit import timeit
        height = self.stdscr.getmaxyx()[0]
        #return timeit(lambda: self.get_displayable_fragments(height), number=n)
        #return timeit(lambda: self.display_on_screen(), number=n)/n
        #return timeit(lambda: self.display_on_screen(self.get_top_screen_fragment()), number=n)/n
        return timeit(lambda: self.display_lines(), number=n)/n
        #return timeit(lambda: self.get_screen_cursor(), number=n)/n


def launch_editor(story: "Story") -> None:
    editor = StoryEditor(story)
    curses.wrapper(editor.run)
