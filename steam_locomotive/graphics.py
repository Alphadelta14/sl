"""Curses handler utilities."""

import contextlib
import curses
import enum
import typing

# shamelessly stole the character derivation from
# https://levelup.gitconnected.com/how-to-convert-an-image-to-ascii-art-with-python-in-5-steps-efbac8996d5e
# to avoid building my own image kernels
ASCII_COV = ' `^",:;Il!i~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$'

#: List of tuples of (color, character)
#: Color may be a grayscale value (0-255) or a palette index
#: Character is the ascii char to show
FrameRowType = typing.List[typing.Tuple[int, str]]
FrameType = typing.List[FrameRowType]
PaletteType = typing.List[int]


class Coloring(enum.Enum):
    GRAYSCALE = "grayscale"
    COLORED_MAX = "colored"
    CURSES_MIN = "curses"


@contextlib.contextmanager
def curses_context():
    """Enter a curses session.

    After this context manager quits (even by error), the session will
    be cleaned up.
    """
    window = curses.initscr()
    try:
        curses.start_color()
        curses.noecho()
        curses.curs_set(0)
        window.nodelay(True)
        window.leaveok(True)
        window.scrollok(False)
        yield window
    finally:
        curses.endwin()


def has_curses() -> bool:
    """Check if curses can be initialized.

    This may not be possible if there is no terminal, for example.
    """
    try:
        with curses_context():
            return True
    except curses.error:
        return False


def get_curses_palette() -> PaletteType:
    """Get a curses 8-color palette."""
    with curses_context():
        palette = []
        for color_id in range(8):
            red, green, blue = curses.color_content(color_id)
            palette += [
                int(red * 255 / 1000),
                int(green * 255 / 1000),
                int(blue * 255 / 1000),
            ]
    return palette


def supports_color_changing() -> bool:
    """Check if term can change colors."""
    with curses_context():
        return curses.can_change_color()


def row_to_curses(
    row: typing.Iterable[int], palette: typing.Optional[PaletteType]
) -> FrameRowType:
    """Convert a row of an image to an ASCII string.

    Parameters
    ----------
    row: typing.List[typing.Tuple[int]]
        pixel buffer data (1d * pal_idx)
    palette: typing.Optional[PaletteType]
        optional RGB palette information

    Returns
    -------
    ascii_str: str
    """
    conv_factor = len(ASCII_COV) / 256.0
    if palette:
        conv_factor /= 3
    curses_data = []
    for value in row:
        if palette:
            brightness = sum(palette[value * 3 : value * 3 + 3])  # r+g+b
        else:
            brightness = value
        weight = ASCII_COV[int(brightness * conv_factor)]
        curses_data.append((value, weight))
    return curses_data
