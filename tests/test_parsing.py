import unittest

from mawaqit_py._parse_helpers import extract_conf_data
from mawaqit_py.parsing import (
    conf_data_from_dict,
    parse_calendar,
    parse_mosque,
    parse_search_results,
)


SAMPLE_MOSQUE = {
    "uuid": "1e77008c-b54b-4a57-aa1c-627368cf8a42",
    "slug": "dzemat-paris",
    "name": "DZEMAT BOSNIAQUES PARIS",
    "type": "MOSQUE",
    "latitude": 48.887,
    "longitude": 2.403,
    "phone": "+33100000000",
    "times": ["04:30", "05:47", "13:55", "18:07", "21:57", "23:27"],
    "iqama": ["+10", "+10", "+10", "+0", "+0"],
    "jumua": "13:00",
    "jumuaAsDuhr": False,
    "localisation": "17 Rue Andre Joineau, 93500",
    "womenSpace": True,
    "parking": False,
}


class MosqueParsingTests(unittest.TestCase):
    def test_parse_mosque_maps_fields(self) -> None:
        mosque = parse_mosque(SAMPLE_MOSQUE)
        self.assertEqual(mosque.uuid, "1e77008c-b54b-4a57-aa1c-627368cf8a42")
        self.assertEqual(mosque.name, "DZEMAT BOSNIAQUES PARIS")
        self.assertEqual(mosque.times.maghrib, "21:57")
        self.assertEqual(mosque.iqama_offsets["fajr"], "+10")
        self.assertEqual(mosque.jumua, "13:00")
        self.assertIs(mosque.women_space, True)
        self.assertIs(mosque.parking, False)
        self.assertEqual(mosque.coordinates, (48.887, 2.403))

    def test_parse_search_results_skips_non_dicts(self) -> None:
        mosques = parse_search_results([SAMPLE_MOSQUE, "junk", None])
        self.assertEqual(len(mosques), 1)
        self.assertEqual(parse_search_results({"not": "a list"}), [])

    def test_parse_search_results_unwraps_envelope(self) -> None:
        mosques = parse_search_results({"data": [SAMPLE_MOSQUE]})
        self.assertEqual(len(mosques), 1)
        self.assertEqual(mosques[0].slug, "dzemat-paris")


class CalendarParsingTests(unittest.TestCase):
    def test_parse_calendar_keys_by_int_day(self) -> None:
        months = [{"1": ["07:05", "08:44", "12:59", "14:48", "17:08", "18:35"]}] + [
            {} for _ in range(11)
        ]
        iqama = [{"1": ["+10", "+10", "+0", "+0", "+5"]}] + [{} for _ in range(11)]
        calendar = parse_calendar(months, iqama)
        self.assertEqual(calendar.day(1, 1).sunrise, "08:44")
        self.assertEqual(calendar.iqama[0][1], ("+10", "+10", "+0", "+0", "+5"))


class ConfDataExtractionTests(unittest.TestCase):
    def test_extract_handles_braces_inside_strings(self) -> None:
        html = (
            "<script>var confData = "
            '{"name": "A } tricky } name", "times": ["1","2","3","4","5","6"]};'
            "</script>"
        )
        blob = extract_conf_data(html)
        self.assertEqual(blob["name"], "A } tricky } name")
        conf = conf_data_from_dict(blob)
        self.assertEqual(conf.name, "A } tricky } name")
        self.assertEqual(conf.times.dhuhr, "3")

    def test_missing_blob_raises(self) -> None:
        with self.assertRaises(ValueError):
            extract_conf_data("<html>no data here</html>")

    def test_skips_placeholder_before_real_assignment(self) -> None:
        html = (
            "<script>window.confData = window.confData || {};</script>"
            '<script>var confData = {"slug": "real", '
            '"times": ["1", "2", "3", "4", "5", "6"]};</script>'
        )
        blob = extract_conf_data(html)
        self.assertEqual(blob["slug"], "real")

    def test_empty_blob_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            conf_data_from_dict({})


if __name__ == "__main__":
    unittest.main()
