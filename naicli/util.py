def join_strings(*strings: str) -> str:
    # when there's only a few of them, it's faster with fstrings (tested on Python 3.9)
    if len(strings) == 2:
        return f"{strings[0]}{strings[1]}"
    elif len(strings) == 3:
        return f"{strings[0]}{strings[1]}{strings[2]}"
    else:
        return "".join(strings)