from __future__ import annotations

import itertools
import typing

# NB: bullseye uses Pillow 8.1.2
from PIL import Image


class Train:
    """A loaded train object.

    The frames object can be a straight buffer to frames (list of list of str)
    or a generator that returns frames (iter of list of str).

    Use Train.from_file() to create one from a GIF.
    """
    def __init__(self, frame_gen: typing.Iterable[typing.List[str]]):
        self.frame_gen = frame_gen

    @classmethod
    def from_gif(cls, handle):
        """Create a Train from a file handle."""
        img = Image.open(handle, formats=["gif", "apng"])
        if not getattr(img, "is_animated", False):
            raise ValueError(f"Expected {img} to be animated")

        def frame_gen():
            for frame_id in range(img.n_frames):
                img.seek(frame_id)
                frame = img.resize((80, 20))
                # convert to black and white
                # TODO: convert to P
                frame = frame.convert("1")
                iter_data = iter(frame.getdata())
                ascii_frame = []
                for row_id in range(20):
                    row = []
                    for value in itertools.islice(iter_data, 80):
                        if value:
                            row.append("#")
                        else:
                            row.append(" ")
                    ascii_frame.append("".join(row))
                yield ascii_frame

        return cls(frame_gen())

    def show(self):
        """Display this train a la curses."""
        for frame in self.frame_gen:
            for row in frame:
                print(row)
