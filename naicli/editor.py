import curses

from typing import List,Tuple,Optional,NewType
from functools import cached_property

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

def split_styled_line(line: StyledLine, at: int) -> Tuple[StyledLine, StyledLine]:
    left: StyledLine = []
    right: StyledLine = []
    i: int = 0
    
    for text,style in line:
        if i >= at:
            right.append((text,style))
        elif i+len(text) <= at:
            left.append((text,style))
        else:
            left.append((text[:at-i], style))
            right.append((text[at-i:], style))
        
        i += len(text)
    
    return left, right

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
        
        self.cursor_line = self.displace_cursor_horizontally(-1)
        self.screen_line, screen_pos = self.displace_cursor_vertically(by=-self.height+1)
        self.screen_line_y = screen_pos//self.width
        self.display_lines()
        
        event_handlers = {
            ord("q"): self.quit,
            curses.KEY_LEFT: self.move_cursor_left,
            curses.KEY_RIGHT: self.move_cursor_right,
            curses.KEY_UP: self.move_cursor_up,
            curses.KEY_DOWN: self.move_cursor_down,
            ord("a"): self.insert_text,
            ord("\n"): self.insert_newline,
        }
        
        if listen_input:
            self.running = True
            while self.running:
                c = stdscr.getch()
                if c in event_handlers: event_handlers[c]()
        
        #print(self.benchmark())
    
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
        self.stdscr.bkgd(" ", curses.color_pair(99) | curses.A_BOLD)
    
    @cached_property
    def height(self):
        return self.stdscr.getmaxyx()[0]-1
    
    @cached_property
    def width(self):
        return self.stdscr.getmaxyx()[1]
    
    def get_screen_cursor(self, destination: Optional[LineCoordinates] = None) -> ScreenCoordinates:
        if destination == None: destination = self.cursor_line
        line_pos: int = min(destination[1], self.line_length(destination[0]))
        x: int = line_pos%self.width
        y: int = self.get_height_from_to(source_line=(self.screen_line, self.screen_line_y), target_line=(destination[0], line_pos//self.width))
        return (y,x)
    
    def get_cursor_line(self, screen_cursor_pos: Optional[ScreenCoordinates] = None) -> LineCoordinates:
        if screen_cursor_pos == None: screen_cursor_pos = self.stdscr.getyx()
        cursor_y, cursor_x = screen_cursor_pos
        cursor_line = (self.screen_line, self.screen_line_y*self.width+cursor_x)
        return self.displace_cursor_vertically(by=cursor_y, from_pos=cursor_line)
    
    def get_height_from_to(self, source_line=Tuple[int,int], target_line=Tuple[int,int]) -> int:
        sign: int = 1
        
        if source_line > target_line: 
            source_line, target_line = target_line, source_line
            sign = -1
        
        return sign * (sum([self.line_height(line) for line in range(source_line[0], target_line[0])]) - source_line[1] + target_line[1])
    
    def scroll_by(self, by: int = 0) -> None:
        top_y, bottom_y = 0,self.height
        self.screen_line, screen_position = self.displace_cursor_vertically(by, from_pos=(self.screen_line, self.screen_line_y*self.width))
        self.screen_line_y = screen_position//self.width
        if by > 0: top_y = self.height-by
        if by < 0: bottom_y = -by+1
        self.stdscr.scroll(by)
        self.display_lines(top_y, bottom_y)
    
    def scroll_to(self, target_line: Optional[Tuple[int,int]] = None) -> None:
        target_line = target_line if target_line else (self.cursor_line[0], self.cursor_line[1]//self.width)
        
        if target_line < (self.screen_line, self.screen_line_y):
            self.screen_line, self.screen_line_y = target_line
        else:
            self.screen_line, screen_position = self.displace_cursor_vertically(by=-self.height+1, 
                from_pos=(target_line[0], target_line[1]*self.width))
            self.screen_line_y = screen_position//self.width
        
        self.stdscr.clear()
        self.display_lines()
    
    def displace_cursor_horizontally(self, by: int=0, from_pos: Optional[LineCoordinates] = None) -> LineCoordinates:
        line_number, position_in_line = from_pos if from_pos else self.cursor_line
        line_length: int = self.line_length(line_number)
        number_of_lines: int = self.get_number_of_lines()
        position_in_line += by
        
        while position_in_line < 0 and line_number > 0:
            by = position_in_line+1
            line_number -= 1
            line_length = self.line_length(line_number)
            position_in_line = line_length + by
        
        while position_in_line > line_length and line_number < number_of_lines-1:
            by = position_in_line - line_length - 1
            line_number += 1
            line_length = self.line_length(line_number)
            position_in_line = by
        
        return min((number_of_lines-1, line_length), max((line_number, position_in_line), (0,0)))
    
    def displace_cursor_vertically(self, by: int=0, from_pos: Optional[LineCoordinates] = None) -> LineCoordinates:
        line_number, position_in_line = from_pos if from_pos else self.cursor_line
        line_y: int = position_in_line//self.width
        line_length: int = self.line_length(line_number)
        line_height: int = line_length//self.width
        number_of_lines: int = self.get_number_of_lines()
        line_y += by
        
        while line_y < 0 and line_number > 0:
            by = line_y+1
            line_number -= 1
            line_length = self.line_length(line_number)
            line_height = line_length//self.width
            line_y = line_height+by
        
        while line_y > line_height and line_number < number_of_lines-1:
            by = line_y - line_height - 1
            line_number += 1
            line_length = self.line_length(line_number)
            line_height = line_length//self.width
            line_y = by
        
        position_in_line = min(line_length, line_y*self.width+(position_in_line%self.width))
        return min((number_of_lines-1, line_length), max((line_number, position_in_line), (0,0)))
        
    def get_line(self, line: int) -> StyledLine:
        raise NotImplemented("Override this method in your editor!")
    
    def get_number_of_lines(self) -> int:
        raise NotImplemented("Override this method in your editor!")
    
    def get_last_position(self) -> LineCoordinates:
        last_line: int = self.get_number_of_lines()-1
        return (last_line, self.line_length(last_line))
    
    def line_length(self, line: int) -> int:
        return sum([len(text) for text,_ in self.get_line(line)])
    
    def line_height(self, line: int):
        return 1+self.line_length(line)//self.width
    
    def draw_cursor(self, cursor_position: Optional[ScreenCoordinates] = None) -> None:
        y,x = cursor_position if cursor_position else self.get_screen_cursor()
        
        if 0 <= y < self.height:
            self.stdscr.move(y,x)
        elif -self.height//2 < y < 0:
            self.scroll_by(y)
        elif self.height <= y < self.height + self.height//2:
            self.scroll_by(y-self.height+1)
        else:
            self.scroll_to((self.cursor_line[0], self.cursor_line[1]//self.width))
    
    def display_lines(self, top_y: Optional[int] = None, bottom_y: Optional[int] = None) -> None:
        bottom_y = bottom_y if bottom_y != None else self.height
        ypos: int = top_y if top_y != None else 0
        xpos: int = 0
        top_line, top_line_y = self.screen_line, self.screen_line_y
        
        if ypos > 0: 
            top_line, top_position = self.displace_cursor_vertically(by=ypos, from_pos=(self.screen_line, self.screen_line_y*self.width))
            top_line_y = top_position//self.width
        
        line_number: int = top_line
        
        while ypos < bottom_y:
            line: StyledLine = self.get_line(line_number)
            length: int = self.line_length(line_number)
            
            if top_line_y > 0 and line_number == top_line:
                # we've gotta trim this line to fit
                to_skip: int = self.width*top_line_y
                line = split_styled_line(line, to_skip)[1]
                length -= to_skip
            
            self.stdscr.move(ypos,xpos)
            
            if length//self.width < self.height-ypos:
                for text,style in line:
                    self.stdscr.addstr(text, style)
            else:
                remaining_space: int = self.get_remaining_screen_space()
            
                for text,style in line:
                    if remaining_space > 0:
                        self.stdscr.addnstr(text, remaining_space, style)
                        remaining_space -= len(text)
            
            ypos += 1+length//self.width
            line_number += 1
        
        self.draw_cursor()
    
    def get_remaining_screen_space(self) -> int:
        y, x = self.stdscr.getyx()
        return self.width*(self.height-y) - x
        #FIXME ideally that -1 shouldn't be there, but i have to deal with a lot of nasty edge cases if i write over the bottom right corner
    
    def move_cursor_right(self, by=1) -> None:
        self.cursor_line = self.displace_cursor_horizontally(by)
        self.draw_cursor()
    
    def move_cursor_left(self, by=1) -> None:
        self.cursor_line = self.displace_cursor_horizontally(-by)
        self.draw_cursor()
    
    def move_cursor_down(self, by=1) -> None:
        self.cursor_line = self.displace_cursor_vertically(by)
        self.draw_cursor()

    def move_cursor_up(self, by=1) -> None:
        self.cursor_line = self.displace_cursor_vertically(-by)
        self.draw_cursor()
    
    def insert_text(self, text: str = "a") -> None:
        pass
    
    def insert_newline(self) -> None:
        pass
    
    
    def benchmark(self, n=10000) -> float:
        from timeit import timeit
        #return timeit(lambda: self.get_displayable_fragments(height), number=n)
        #return timeit(lambda: self.display_on_screen(), number=n)/n
        #return timeit(lambda: self.display_on_screen(self.get_top_screen_fragment()), number=n)/n
        #return timeit(lambda: self.display_lines(), number=n)/n
        #return timeit(lambda: self.get_screen_cursor(), number=n)/n
        
        def bench_scroll():
            screen_line, screen_line_position = self.screen_line, self.screen_line_y*self.width
            self.cursor_line = self.displace_cursor_vertically(by=self.height, from_pos=(screen_line, screen_line_position))
            self.draw_cursor()
            self.cursor_line = self.screen_line, screen_line_position
            self.draw_cursor()
        
        return timeit(bench_scroll, number=n)/n

class BufferEditor(Editor):
    def __init__(
        self,
        text: str = "",
    ):
        super(BufferEditor,self).__init__()
        self.lines: List[str] = split_lines(text)
        self.cursor_line: LineCoordinates = (0,0)
        self.stdscr = None
    
    def reset(self) -> None:
        self.lines = [""]
        self.cursor_line = (0,0)
    
    def is_empty(self) -> bool:
        return len(self.lines) == 1 and self.lines[0] == ""
    
    def get_line(self, line: int) -> StyledLine:
        return [(self.lines[line], curses.color_pair(99) | curses.A_BOLD)] if 0 <= line < len(self.lines) else []
    
    def get_number_of_lines(self) -> int:
        return len(self.lines)
    
    def get_text(self) -> str:
        return "\n".join(self.lines)
    
    def insert_text(self, text: str = "a") -> None:
        line_number, position_in_line = self.cursor_line
        
        if 0 <= line_number < len(self.lines):
            line: str = self.lines[line_number]
            self.lines[line_number] = join_strings(line[:position_in_line], text, line[position_in_line:])
            self.cursor_line = (line_number, position_in_line+len(text))
            
            if self.stdscr != None:
                self.stdscr.clrtobot()
                self.display_lines(top_y=self.get_screen_cursor()[0])
    
    def insert_newline(self) -> None:
        line_number, position_in_line = self.cursor_line
        
        if 0 <= line_number < len(self.lines):
            if position_in_line <= 0:
                self.lines.insert(line_number, "")
            elif position_in_line >= self.line_length(line_number):
                self.lines.insert(line_number+1, "")
            else:
                line: str = self.lines[line_number]
                self.lines[line_number:line_number+1] = [line[:position_in_line], line[position_in_line:]]
            
            self.cursor_line = (line_number+1, 0)
            
            if self.stdscr != None:
                self.stdscr.clrtobot()
                self.display_lines(top_y=self.get_screen_cursor()[0])

class StoryEditor(Editor):
    def __init__(
        self,
        story: "Story",
    ):
        super(StoryEditor,self).__init__()
        self.story: "Story" = story
        self.buffer = BufferEditor()
        self.buffer_line: LineCoordinates = (0,0)
        self.cursor_line: LineCoordinates = (fragment_to_position(story, len(story.fragments), get_data=get_fragment_heights)+1, 0)
    
    def run(self, stdscr, listen_input: bool = True):
        get_fragment_infos(self.story.fragments)
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
        buffer_offset: int = 0
        
        if not self.buffer.is_empty() and line > self.buffer_line[0]:
            # the case for the first line of the buffer is considered later
            max_buffer_line: int = self.buffer.get_number_of_lines()-1
            buffer_offset = max_buffer_line
            
            if line-self.buffer_line[0] < max_buffer_line:
                # we're inside the buffer, past its first line but before reaching the last one!
                return self.buffer.get_line(line-self.buffer_line[0])
        
        fragment_number, relative_line = line_to_fragment(self.story, line-buffer_offset)
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
        
        if not self.buffer.is_empty():
            max_buffer_line: int = self.buffer.get_number_of_lines()-1
            
            if line == self.buffer_line[0] or line-self.buffer_line[0] == max_buffer_line:
                # we're either at the first or last line of the buffer, must split
                left, right = split_styled_line(line_chunks, self.buffer_line[1])
                line_chunks = []
                
                if line == self.buffer_line[0]:
                    # we must insert the first line of the buffer at the end
                    line_chunks = left
                
                line_chunks.extend(self.buffer.get_line(line-self.buffer_line[0]))
                
                if line-self.buffer_line[0] == max_buffer_line:
                    # we are at the last line of the buffer, append the rest of the fragments
                    line_chunks.extend(right)
        
        return line_chunks
    
    def get_number_of_lines(self) -> int:
        return 1 + fragment_to_position(self.story, len(self.story.fragments), get_data=get_fragment_heights) + \
            self.buffer.get_number_of_lines()-1

    def benchmark(self, n=10000) -> float:
        from timeit import timeit
        #return timeit(lambda: self.get_displayable_fragments(height), number=n)
        #return timeit(lambda: self.display_on_screen(), number=n)/n
        #return timeit(lambda: self.display_on_screen(self.get_top_screen_fragment()), number=n)/n
        #return timeit(lambda: self.display_lines(), number=n)/n
        #return timeit(lambda: self.get_screen_cursor(), number=n)/n
    
    def buffer_to_line(self, buffer_position: Optional[LineCoordinates] = None) -> LineCoordinates:
        buffer_position = buffer_position if buffer_position != None else self.buffer.cursor_line
        return (self.buffer_line[0] + buffer_position[0], 
            self.buffer_line[1] + buffer_position[1] if buffer_position[0] == 0 else buffer_position[1])
    
    def line_to_buffer(self, absolute_position: Optional[LineCoordinates] = None) -> LineCoordinates:
        absolute_position = absolute_position if absolute_position != None else self.cursor_line
        return (absolute_position[0] - self.buffer_line[0], 
            absolute_position[1] - self.buffer_line[1] if absolute_position[0] == self.buffer_line[0] else absolute_position[1])
    
    def is_cursor_in_buffer(self) -> bool:
        return (0,0) <= self.line_to_buffer() <= self.buffer.get_last_position()
    
    def reset_buffer(self) -> None:
        if not self.buffer.is_empty():
            fragment_number, relative_line = line_to_fragment(self.story, self.buffer_line[0])
            fragment_info: "FragmentInfo" = get_fragment_info(self.story.fragments[fragment_number])
            line_position: int = fragment_info.line_to_pos(relative_line)
            position_in_fragment: int = line_position + self.buffer_line[1]
            origin: "Origin" = Origin.edit
            last_line: int = fragment_to_position(self.story, len(self.story.fragments), get_data=get_fragment_heights)
            
            if self.buffer_line >= (last_line, fragment_info.line_lengths[relative_line]):
                # we are at the end of a text, it's a "user" origin instead of edit!
                origin = Origin.user
            
            absolute_position: int = fragment_to_position(self.story, fragment_number) + position_in_fragment
            insert_text(self.story, self.buffer.get_text(), absolute_position, origin=origin)
        
        
        self.buffer.reset()
        self.buffer_line = self.cursor_line
    
    def draw_cursor(self, cursor_position: Optional[ScreenCoordinates] = None) -> None:
        if not self.is_cursor_in_buffer():
            self.reset_buffer()
        
        super(StoryEditor,self).draw_cursor(cursor_position)
    
    def insert_text(self, text: str = "a") -> None:
        if not self.is_cursor_in_buffer():
            self.reset_buffer()
        else:
            self.buffer.cursor_line = self.line_to_buffer()
        
        self.buffer.insert_text(text)
        self.cursor_line = self.buffer_to_line()
        self.stdscr.clrtobot()
        self.display_lines(top_y=self.get_screen_cursor()[0])
    
    def insert_newline(self) -> None:
        if not self.is_cursor_in_buffer():
            self.reset_buffer()
        else:
            self.buffer.cursor_line = self.line_to_buffer()
        
        self.buffer.insert_newline()
        self.cursor_line = self.buffer_to_line()
        self.stdscr.clrtobot()
        self.display_lines(top_y=self.get_screen_cursor()[0])
    


def launch_editor(story: "Story") -> None:
    editor = StoryEditor(story)
    #editor = BufferEditor(text=assemble_story_fragments(story.fragments))
    curses.wrapper(editor.run)
