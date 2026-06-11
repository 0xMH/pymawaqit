"""Live tests that hit the real MAWAQIT API. Skipped unless MAWAQIT_LIVE=1."""

import os
import unittest

from pymawaqit import Mawaqit


LIVE = os.environ.get("MAWAQIT_LIVE") == "1"


@unittest.skipUnless(LIVE, "set MAWAQIT_LIVE=1 to run live tests")
class LiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = Mawaqit()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.client.close()

    def test_search_by_city(self) -> None:
        mosques = self.client.search("paris")
        self.assertTrue(mosques)
        first = mosques[0]
        self.assertTrue(first.name)
        self.assertTrue(first.slug)
        self.assertEqual(len(list(first.times.prayers)), 5)

    def test_search_by_coords(self) -> None:
        mosques = self.client.nearby(48.8566, 2.3522)
        self.assertTrue(mosques)

    def test_calendar_has_twelve_months(self) -> None:
        mosques = self.client.search("paris")
        calendar = self.client.calendar(mosques[0])
        self.assertEqual(len(calendar.months), 12)
        self.assertIsNotNone(calendar.day(1, 1))


if __name__ == "__main__":
    unittest.main()
