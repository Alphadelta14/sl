from __future__ import annotations

import curses
import itertools
import time
import typing

# NB: bullseye uses Pillow 8.1.2
from PIL import Image

from .graphics import curses_context, row_to_curses, get_curses_palette

MAX_COLUMNS = 100
MAX_ROWS = 40


class Train:
    """A loaded train object.

    The frames object can be a straight buffer to frames (list of list of str)
    or a generator that returns frames (iter of list of str).

    Use Train.from_file() to create one from a GIF.
    """
    def __init__(self, frame_gen: typing.Iterable[typing.List[str]], palette: typing.List[int]):
        self.frame_gen = frame_gen
        self.palette = palette

    @classmethod
    def from_gif(cls, handle):
        """Create a Train from a file handle."""
        img = Image.open(handle, formats=["gif", "apng"])
        if not getattr(img, "is_animated", False):
            raise ValueError(f"Expected {img} to be animated")

        # sample = img.convert("P", palette=Image.Palette.ADAPTIVE, colors=16)
        sample = img.quantize(colors=64)
        palette = sample.getpalette()
        sample = Image.new("P", (16, 16))
        # sample.putpalette(get_curses_palette())
        sample.putpalette(palette)
        aspect_ratio = min(MAX_COLUMNS / img.size[0], MAX_ROWS / img.size[1])
        new_width = int(aspect_ratio*img.size[0])
        new_height = int(aspect_ratio*img.size[1])

        def frame_gen():
            for frame_id in range(img.n_frames):
                img.seek(frame_id)
                frame = img.resize((new_width, new_height))
                # convert to black and white
                # TODO: convert to P
                # frame = frame.convert("L")
                frame = frame.convert("RGB")
                frame = frame.quantize(colors=256, palette=sample)
                # frame = frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=16)
                palette = frame.getpalette()
                iter_data = iter(frame.getdata())
                ascii_frame = []
                for row_id in range(new_height):
                    row = row_to_curses(itertools.islice(iter_data, new_width), palette)
                    ascii_frame.append(row)
                yield ascii_frame

        return cls(frame_gen(), palette)

    def show(self):
        """Display this train a la curses."""
        # frame, palette = next(self.frame_gen)
        # print(self.palette)
        # return
        with curses_context() as window:
            for pal_pos in range(0, len(self.palette), 3):
                color_id = pal_pos // 3
                red, green, blue = self.palette[pal_pos:pal_pos+3]
                curses.init_color(color_id, int(red*1000/255), int(green*1000/255), int(blue*1000/255))
                curses.init_pair(color_id+1, color_id, 0)
            for frame in self.frame_gen:
                for row_id, row in enumerate(frame):
                    for col_id, data in enumerate(row):
                        color, weight = data
                        window.addch(row_id, col_id, weight, curses.color_pair(color+1))
                        # window.addch(row_id, col_id, weight)
                window.getch()
                window.refresh()
                time.sleep(0.1)
