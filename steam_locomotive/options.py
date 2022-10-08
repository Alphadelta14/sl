"""Attributes of our train."""

from .graphics import Coloring


class TrainOptions:
    """Hold options.

    These are populated in cli.main.
    """

    # Setup slots to ensure state is fairly consistent between structures.
    __slots__ = ("flying", "accident", "little", "number", "gif", "colored")

    def __init__(self):
        #: Fly off the screen
        self.flying: bool = False
        #: People cry out for help
        self.accident: bool = False
        #: Little train
        self.little: bool = False
        #: Selected train. -1 to use random
        self.number: int = -1
        #: Path to gif to use
        self.gif: str = ""
        #: Coloring to use
        self.colored = Coloring.GRAYSCALE
