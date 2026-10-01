import unittest

from utils.formatting import format_size


class TestFormatting(unittest.TestCase):
    def test_bytes(self):
        self.assertEqual(format_size(500), "500.00 B")

    def test_kilobytes(self):
        self.assertEqual(format_size(1024), "1.00 KB")

    def test_megabytes(self):
        self.assertEqual(format_size(1024 ** 2), "1.00 MB")

    def test_none(self):
        self.assertEqual(format_size(None), "Unavailable")


if __name__ == "__main__":
    unittest.main()
