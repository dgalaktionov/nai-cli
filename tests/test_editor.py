import os
import pytest
import curses

from time import sleep
from itertools import accumulate

from naicli.story_model import *
from naicli.story import open_story_file
from naicli.editor import *

@pytest.fixture(scope="module")
def book():
    return open_story_file("example/grug.story")

@pytest.fixture(scope="module")
def story(book):
    return book.content.story

@pytest.fixture(scope="module")
def editor(story):
    return StoryEditor(story)

def run_and_test(editor, assertion):
    stdscr = curses.initscr()
    editor.run(stdscr, listen_input=False)
    assertion(editor)
    editor.quit()

def editor_initializes(e):
    height, width = e.stdscr.getmaxyx()
    assert height > 0 and width > 0
    

def editor_cursor(e):
    height, width = e.stdscr.getmaxyx()
    screen_y, screen_x = e.stdscr.getyx()
    assert 0 <= screen_y < height
    assert 0 <= screen_x < width
    assert e.get_screen_cursor() == (screen_y, screen_x)
    assert e.get_cursor_line() == e.cursor_line
    assert e.get_screen_cursor() == e.get_screen_cursor(e.get_cursor_line())
    assert e.get_cursor_line() == e.get_cursor_line(e.get_screen_cursor())
    
    line_number = e.screen_line
    line_pos = e.screen_line_y*width
    line = e.get_line(line_number)
    line_length = e.line_length(line)
    line_chunk, chunk_pos = next(((i, len(line[i][0])+line_pos-l) for i,l in enumerate(accumulate(len(text) for text,_ in line)) if l > line_pos), (0,0))
    number_of_lines = e.get_number_of_lines()
    max_y: int = 0
    
    for y in range(height):
        after_end: bool = False
        
        if line_number < number_of_lines-1:
            max_y = y
            
            if line_pos > line_length:
                line_pos = 0
                line_number += 1
                line = e.get_line(line_number)
                line_length = e.line_length(line)
                line_chunk = 0
                chunk_pos = 0
        
        for x in range(width):
            c = e.stdscr.instr(y,x,1)
            
            if line_pos >= line_length:
                assert c == b" "
                assert e.get_screen_cursor((line_number, min(line_pos,line_length))) == (max_y, min(line_pos,line_length)%width)
                assert e.get_cursor_line((y,x)) == ((line_number+1, 0) if after_end else (line_number, line_length))
                after_end = line_number < number_of_lines-1
                if line_pos == line_length: line_pos += 1
            else:
                while chunk_pos >= len(line[line_chunk][0]):
                    line_chunk += 1
                    chunk_pos = 0
                
                assert c == line[line_chunk][0][chunk_pos].encode()
                assert e.get_screen_cursor((line_number, line_pos)) == (y,x)
                assert e.get_cursor_line((y,x)) == (line_number, line_pos)
                chunk_pos += 1
                line_pos += 1

def test_editor(editor):
    run_and_test(editor, editor_initializes)
    run_and_test(editor, editor_cursor)
