from __future__ import annotations

import argparse
import sys
import typing

from .graphics import Coloring
from .options import TrainOptions
from .train import Train


def main(argv: typing.Optional[typing.List[str]] = None) -> int:
    """Handle invocation as a program.

    This parses arguments and invokes the appropriate actions.

    Returns
    ------
    exit_code : int
    """
    parser = argparse.ArgumentParser(prog="sl")
    # NB: These are set on a TrainOptions instance
    parser.add_argument(
        "-F", dest="flying", help="Fly off the screen", action="store_true"
    )
    parser.add_argument(
        "-a", dest="accident", help="People cry out for help", action="store_true"
    )
    parser.add_argument(
        "-l", dest="little", help="Show a little train", action="store_true"
    )
    parser.add_argument(
        "-n", dest="number", help="Select which train to use (default random)", type=int
    )
    parser.add_argument(
        "--term-colors",
        dest="colored",
        help="Use 8-color color palette",
        action="store_const",
        const=Coloring.CURSES_MIN,
    )
    parser.add_argument(
        "--max-colors",
        dest="colored",
        help="Use 64-color color palette",
        action="store_const",
        const=Coloring.COLORED_MAX,
    )
    parser.add_argument(
        "--grayscale",
        dest="colored",
        help="Use 64-color color palette",
        action="store_const",
        const=Coloring.GRAYSCALE,
    )
    parser.add_argument("--gif", help="Path to gif to use for train")
    args = TrainOptions()
    parser.parse_args(argv, args)
    train = Train.select_train(args)
    train.show()
    return 0


if __name__ == "__main__":
    sys.exit(main())
