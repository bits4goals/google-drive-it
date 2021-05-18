import unittest
import url
import itertools
import random
import string
import itertools


class TestUrl(unittest.TestCase):

    def setUpClass(self):
        pass


    def tearDownClass(self):
        pass


    def setUp(self):
        pass


    def tearDown(self):
        pass


    @staticmethod
    def test_urls():
        """Generate URLs."""

        protocols = ['', 'file:///', 'ftp://', 'http://', 'https://']
        paths = ['', 'home', 'home/foo', 'home/foo/bar.txt']
        params = ['', '?abc=cde', '?abc=cde&FgH=iJk!@#$%']
        randoms = ['', ''.join(random.choices(string.ascii_letters, k=32))]

        for test_url in itertools.product(protocols, paths, params, randoms):
            yield ''.join(test_url)


    def test_init(self):
        """New instance has the proper attributes with the proper
        values."""

        # instantiate with controlled URL

        # test attributes from the instance (including URL)

        for test_url in self.test_urls():
            with self.subTest(test_url=test_url):
                self.assertEqual(test_url, url.Url(test_url).url)


if __name__ == '__main__':
    unittest.main()
