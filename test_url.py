import unittest
import url
import itertools
import random
import string
import itertools


class TestUrlInit(unittest.TestCase):
    """Url instantiation."""

    @staticmethod
    def urls():
        """URL generator."""

        protocols = ['', 'file:///', 'ftp://', 'http://', 'https://']
        paths = ['', 'home', 'home/foo', 'home/foo/bar.txt']
        params = ['', '?abc=cde', '?abc=cde&FgH=iJk!@#$%']
        randoms = ['', ''.join(random.choices(string.ascii_letters, k=32))]

        for test_url in itertools.product(protocols, paths, params, randoms):
            yield ''.join(test_url)


    def test_url(self):
        """Instantiation with URL preserves received value."""

        for test_url in self.urls():
            with self.subTest(test_url=test_url):
                self.assertEqual(test_url, url.Url(test_url).url)


class TestUrlHiddenAttributes(unittest.TestCase):
    """Attributes prefixed with ‘_’ work correctly.

    These attributes are:

    _responseurl
    _urlpath
    _basename_f
    """

    pass
if __name__ == '__main__':
    unittest.main()
