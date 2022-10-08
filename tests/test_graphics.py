import curses
import unittest

from steam_locomotive import graphics

SUPPORTS_CURSES = graphics.has_curses()


class TestGraphics(unittest.TestCase):
    def test_row_to_ascii_empty(self):
        assert graphics.row_to_curses([], palette=None) == []

    def test_row_to_ascii(self):
        assert graphics.row_to_curses([0, 255, 127], palette=None) == [
            (0, " "),
            (255, "$"),
            (127, "u"),
        ]

    if SUPPORTS_CURSES:

        def test_context(self):
            assert curses.isendwin()
            with graphics.curses_context():
                assert not curses.isendwin()
            assert curses.isendwin()

        def test_broken_context(self):
            assert curses.isendwin()
            try:
                with graphics.curses_context():
                    assert not curses.isendwin()
                    raise ValueError()
            except ValueError:
                assert curses.isendwin()
            else:
                # don't expect to get here
                assert False
