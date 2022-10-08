"""Handle trains.

Main entrypoint is in .cli.
"""
from __future__ import annotations

import curses
import itertools
import logging
import pathlib
import random
import time
import typing

# NB: bullseye uses Pillow 8.1.2
from PIL import Image, ImageEnhance

from . import data as data_package
from . import graphics
from .graphics import curses_context, row_to_curses
from .options import TrainOptions

MAX_COLUMNS = 100
MAX_ROWS = 40


class Train:
    """A loaded train object.

    The frames object can be a straight buffer to frames (list of list of str)
    or a generator that returns frames (iter of list of str).

    Use Train.from_file() to create one from a GIF.
    """

    def __init__(
        self,
        frame_gen: typing.Iterable[graphics.FrameType],
        palette: typing.Optional[graphics.PaletteType] = None,
    ):
        #: Iterator for frame generation
        self.frame_gen = frame_gen
        #: Optional color palette
        self.palette = palette
        #: Render speed (time between frames)
        self.frame_speed = 0.1

    @classmethod
    def select_train(cls, options: TrainOptions) -> Train:
        """Get a selected train based on options passed to command line.

        Returns
        -------
        train: Train
        """
        if options.gif:
            filename = pathlib.Path(options.gif)
        else:
            filenames = sorted(pathlib.Path(data_package.__file__).parent.glob("*.gif"))
            if options.number == -1:
                filename = random.choice(filenames)
            else:
                filename = filenames[options.number % len(filenames)]
        return cls.from_gif(filename, options.colored)

    @classmethod
    def from_gif(
        cls,
        handle: typing.Union[str, pathlib.Path],
        colored=graphics.Coloring.GRAYSCALE,
    ) -> Train:
        """Create a Train from a file handle.

        Parameters
        ----------
        handle: typing.Union[str, pathlib.Path]
            GIF handle or filename to load from
        colored: graphics.Coloring
            Palette mode to generate

        Returns
        -------
        train: Train
        """
        img = Image.open(handle, formats=["GIF"])
        if not getattr(img, "is_animated", False):
            raise ValueError(f"Expected {img} to be animated")

        # sample = img.convert("P", palette=Image.Palette.ADAPTIVE, colors=16)
        sample = img.convert("RGB")
        contraster = ImageEnhance.Contrast(sample)
        sample = contraster.enhance(2.5)
        sample_palette = None
        if colored == graphics.Coloring.COLORED_MAX:
            if graphics.supports_color_changing():
                sample = sample.quantize(colors=64)
                palette = sample.getpalette()
                assert palette
                sample_palette = Image.new("P", (16, 16))
                sample_palette.putpalette(palette)
            else:
                logging.warning("Can't change colors, falling back to grayscale")
                colored = graphics.Coloring.GRAYSCALE
        elif colored == graphics.Coloring.CURSES_MIN:
            if graphics.supports_color_changing():
                palette = graphics.get_curses_palette()
                sample_palette = Image.new("P", (16, 16))
                sample_palette.putpalette(palette)
            else:
                logging.warning("Can't change colors, falling back to grayscale")
                colored = graphics.Coloring.GRAYSCALE
        if colored == graphics.Coloring.GRAYSCALE:
            palette = None
        # FIXME: Also handle that chars are already 1/2wide
        aspect_ratio = min(MAX_COLUMNS / img.size[0], MAX_ROWS / img.size[1])
        new_width = int(aspect_ratio * img.size[0])
        new_height = int(aspect_ratio * img.size[1])

        def frame_gen() -> typing.Iterator[graphics.FrameType]:
            """Iterate through frames.

            Yields
            ------
            frame: graphics.FrameType
                A GIF frame, encoded as a rows x columns 2d array.
                Each point is a palette idx and an ascii char.
            """
            for frame_id in range(img.n_frames):
                img.seek(frame_id)
                frame = img.resize((new_width, new_height))
                if colored == graphics.Coloring.GRAYSCALE:
                    # convert to black and white (single band)
                    frame = frame.convert("L")
                    local_palette = None
                else:
                    frame = frame.convert("RGB")
                    contraster = ImageEnhance.Contrast(frame)
                    frame = contraster.enhance(2.5)
                    frame = frame.quantize(colors=64, palette=sample_palette)
                    # frame = frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=16)
                    local_palette = frame.getpalette()
                iter_data = iter(frame.getdata())
                ascii_frame = []
                for row_id in range(new_height):
                    row = row_to_curses(
                        itertools.islice(iter_data, new_width), local_palette
                    )
                    ascii_frame.append(row)
                yield ascii_frame

        return cls(frame_gen(), palette)

    def show(self):
        """Display this train a la curses."""
        # Debug tip::
        #   frame = next(self.frame_gen)
        #   (this can be called outside of curses_context!)
        with curses_context() as window:
            # initialize the color pairs for this session
            if self.palette:
                for pal_pos in range(0, len(self.palette), 3):
                    color_id = pal_pos // 3
                    red, green, blue = self.palette[pal_pos : pal_pos + 3]
                    try:
                        curses.init_color(
                            color_id,
                            int(red * 1000 / 255),
                            int(green * 1000 / 255),
                            int(blue * 1000 / 255),
                        )
                    except curses.error:
                        raise ValueError(
                            f"Couldn't initialize color {color_id} ({red}, {green}, {blue})"
                        )
                    # NB: pair_id=0 is reserved and errors if used
                    curses.init_pair(color_id + 1, color_id, 0)
            frame: graphics.FrameType
            row: graphics.FrameRowType
            for frame in self.frame_gen:
                for row_id, row in enumerate(frame):
                    for col_id, data in enumerate(row):
                        color, weight = data
                        if self.palette:
                            # our pair_id is just one higher than our palette idx
                            window.addch(
                                row_id, col_id, weight, curses.color_pair(color + 1)
                            )
                        else:
                            window.addch(row_id, col_id, weight)
                window.getch()
                window.refresh()
                time.sleep(self.frame_speed)
