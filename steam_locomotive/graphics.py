"""Curses handler utilities."""

import contextlib
import curses
import typing

# shamelessly stole the character derivation from
# https://levelup.gitconnected.com/how-to-convert-an-image-to-ascii-art-with-python-in-5-steps-efbac8996d5e
# to avoid building my own image kernels
ASCII_COV = " `^\",:;Il!i~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
CONV_FACTOR = len(ASCII_COV) / 256.0 / 3


@contextlib.contextmanager
def curses_context():
    window = curses.initscr()
    try:
        curses.noecho()
        curses.curs_set(0)
        window.nodelay(True)
        window.leaveok(True)
        window.scrollok(False)
        if curses.has_colors():
            curses.start_color()
        yield window
    finally:
        curses.endwin()


def get_curses_palette():
    """Get a curses 8-color palette."""
    with curses_context():
        palette = []
        for color_id in range(64):
            red, green, blue = curses.color_content(color_id)
            palette += [int(red * 255 / 1000), int(blue * 255 / 1000), int(green * 255 / 1000)]
    return palette


def row_to_curses(row: typing.List[int], palette: typing.List[int]) -> str:
    """Convert a row of an image to an ASCII string.

    Parameters
    ----------
    row: typing.List[typing.Tuple[int, int, int]]
        pixel buffer data (1d * RGB)

    Returns
    -------
    ascii_str: str
    """
    curses_data = []
    for color in row:
        brightness = sum(palette[color*3:color*3+3])  # r+g+b
        weight = ASCII_COV[int(brightness * CONV_FACTOR)]
        curses_data.append((color, weight))
    return curses_data
