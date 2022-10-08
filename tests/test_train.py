import pathlib
import unittest

from steam_locomotive import data as data_package
from steam_locomotive.graphics import Coloring
from steam_locomotive.train import Train


class TestTrain(unittest.TestCase):
    def setUp(self):
        self.gif_path = pathlib.Path(data_package.__file__).parent.joinpath(
            "animated-train-image-0018.gif"
        )

    def test_gif_exists(self):
        assert self.gif_path.exists()

    def test_train_frame_gen(self):
        train = Train.from_gif(self.gif_path, Coloring.GRAYSCALE)
        assert not train.palette, "no palette for grayscale"
        # animated-train-image-0018.gif has 8 frames
        assert len(list(train.frame_gen)) == 8
