import unittest
import url as urlm
import itertools
import random
import string
import itertools


def urls_for_test():
    """URL generator."""

    protocols = ['', 'file:///', 'ftp://', 'http://', 'https://']
    paths = ['', 'home', 'home/foo', 'home/foo/bar.txt']
    params = ['', '?abc=cde', '?abc=cde&FgH=iJk!@#$%']
    randoms = ['', ''.join(random.choices(string.ascii_letters, k=32))]

    for comb in itertools.product(protocols, paths, params, randoms):
        yield ''.join(comb)


class TestUrlInit(unittest.TestCase):
    """Url instantiation."""

    def test_attr_url(self):
        """Instantiation with URL preserves received value."""

        for url in urls_for_test():
            with self.subTest(url=url):
                self.assertEqual(url, urlm.Url(url).url)


class TestAttr_ResponseUrl(unittest.TestCase):
    """Attribute works correctly."""

    def test__responseurl_must_be_set_first(self):
        """Raises error if trying to get _responseurl before setting it."""

        with self.assertRaises(RuntimeError):
            urlm.Url('')._responseurl


    def test__responseurl_get(self):
        """‘get’ works properly for ‘_responseurl’."""

        url_obj = urlm.Url('')
        for url in urls_for_test():
            with self.subTest(url=url):
                url_obj._responseurl = url
                self.assertEqual(url_obj._responseurl, url)


if __name__ == '__main__':
    unittest.main()
