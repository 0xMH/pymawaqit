import unittest

from mawaqit_py import Announcement, Calendar, Mosque, PrayerTimes


class PrayerTimesTests(unittest.TestCase):
    def test_from_list_separates_sunrise_from_prayers(self) -> None:
        times = PrayerTimes.from_list(
            ["04:30", "05:47", "13:55", "18:07", "21:57", "23:27"]
        )
        self.assertEqual(times.fajr, "04:30")
        self.assertEqual(times.sunrise, "05:47")
        self.assertEqual(times.isha, "23:27")
        self.assertNotIn("sunrise", times.prayers)
        self.assertEqual(list(times.prayers), ["fajr", "dhuhr", "asr", "maghrib", "isha"])
        self.assertEqual(times.prayers["dhuhr"], "13:55")

    def test_from_list_tolerates_short_input(self) -> None:
        times = PrayerTimes.from_list(["04:30", "05:47"])
        self.assertEqual(times.fajr, "04:30")
        self.assertIsNone(times.isha)

    def test_subscript_and_iter(self) -> None:
        times = PrayerTimes.from_list(["1", "2", "3", "4", "5", "6"])
        self.assertEqual(times["asr"], "4")
        with self.assertRaises(KeyError):
            times["zuhr"]
        self.assertEqual(dict(times)["sunrise"], "2")


class MosqueTests(unittest.TestCase):
    def test_iqama_offsets_map_to_prayers(self) -> None:
        mosque = Mosque(iqama=("+10", "+10", "+0", "+0", "+5"))
        self.assertEqual(
            mosque.iqama_offsets,
            {"fajr": "+10", "dhuhr": "+10", "asr": "+0", "maghrib": "+0", "isha": "+5"},
        )

    def test_coordinates_and_url(self) -> None:
        mosque = Mosque(slug="some-mosque", latitude=48.887, longitude=2.403)
        self.assertEqual(mosque.coordinates, (48.887, 2.403))
        self.assertEqual(mosque.url, "https://mawaqit.net/en/some-mosque")

    def test_facilities_only_lists_true_flags(self) -> None:
        mosque = Mosque(women_space=True, parking=False, ablutions=True)
        self.assertEqual(mosque.facilities, {"women_space": True, "ablutions": True})

    def test_to_dict_drops_raw_by_default(self) -> None:
        mosque = Mosque(name="X", raw={"a": 1})
        data = mosque.to_dict()
        self.assertNotIn("raw", data)
        self.assertIn("raw", mosque.to_dict(include_raw=True))


class CalendarTests(unittest.TestCase):
    def test_day_lookup_is_one_based(self) -> None:
        july = {1: PrayerTimes.from_list(["07", "08", "13", "15", "17", "18"])}
        months = tuple({} for _ in range(12))
        months = (*months[:6], july, *months[7:])
        calendar = Calendar(months=months)
        self.assertEqual(calendar.day(7, 1).dhuhr, "13")
        self.assertIsNone(calendar.day(7, 2))
        self.assertIsNone(calendar.day(13, 1))


if __name__ == "__main__":
    unittest.main()
