import unittest

from xfinder.eval import main as evaluate


class TestxFinderEval(unittest.TestCase):

    def test_accuracy_calculation(self):
        # Dummy test
        config_path = 'path/to/test_config.yaml'
        accuracy = evaluate(config_path)
        self.assertTrue(0 <= accuracy <= 1)


if __name__ == '__main__':
    unittest.main()
