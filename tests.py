import unittest


class MyTestCase(unittest.TestCase):
    def test_help(self):
        self.assertEqual(help('!help'),self.help_message)  # add assertion here

if __name__ == '__main__':
    unittest.main()
