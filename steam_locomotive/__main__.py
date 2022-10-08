"""Support `python -m steam_locomotive` invocation."""
import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
