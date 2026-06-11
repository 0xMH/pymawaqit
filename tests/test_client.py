import unittest

from pymawaqit import Mawaqit, Mosque


class SearchParamTests(unittest.TestCase):
    def test_requires_word_or_coords(self) -> None:
        with self.assertRaises(ValueError):
            Mawaqit._search_params(word=None, lat=None, lon=None, page=1)

    def test_lat_lon_must_come_together(self) -> None:
        with self.assertRaises(ValueError):
            Mawaqit._search_params(word=None, lat=48.0, lon=None, page=1)

    def test_word_search_params(self) -> None:
        params = Mawaqit._search_params(word="paris", lat=None, lon=None, page=2)
        self.assertEqual(params, {"page": 2, "word": "paris"})

    def test_coord_search_params(self) -> None:
        params = Mawaqit._search_params(word=None, lat=48.85, lon=2.35, page=1)
        self.assertEqual(params, {"page": 1, "lat": 48.85, "lon": 2.35})

    def test_page_must_be_positive(self) -> None:
        with self.assertRaises(ValueError):
            Mawaqit._search_params(word="paris", lat=None, lon=None, page=0)


class _FakeClient(Mawaqit):
    def __init__(self, pages: list[list[Mosque]]) -> None:
        self._pages = iter(pages)

    def search(self, *_args, page: int = 1, **_kwargs) -> list[Mosque]:
        return next(self._pages, [])


class IterSearchTests(unittest.TestCase):
    def _client_returning(self, pages: list[list[Mosque]]) -> Mawaqit:
        return _FakeClient(pages)

    def test_stops_when_pages_repeat(self) -> None:
        same = [Mosque(uuid="a"), Mosque(uuid="b")]
        client = self._client_returning([list(same), list(same), list(same)])
        results = list(client.iter_search("x"))
        self.assertEqual([m.uuid for m in results], ["a", "b"])

    def test_dedups_overlap_across_pages(self) -> None:
        client = self._client_returning(
            [[Mosque(uuid="a"), Mosque(uuid="b")], [Mosque(uuid="b"), Mosque(uuid="c")]]
        )
        results = list(client.iter_search("x"))
        self.assertEqual([m.uuid for m in results], ["a", "b", "c"])


class SlugResolutionTests(unittest.TestCase):
    def test_slug_from_mosque(self) -> None:
        self.assertEqual(Mawaqit._slug(Mosque(slug="abc")), "abc")

    def test_slug_from_string(self) -> None:
        self.assertEqual(Mawaqit._slug("  abc  "), "abc")

    def test_slug_from_url(self) -> None:
        url = "https://mawaqit.net/en/grande-mosquee-de-paris?x=1"
        self.assertEqual(Mawaqit._slug(url), "grande-mosquee-de-paris")

    def test_mosque_without_slug_raises(self) -> None:
        with self.assertRaises(ValueError):
            Mawaqit._slug(Mosque())


if __name__ == "__main__":
    unittest.main()
