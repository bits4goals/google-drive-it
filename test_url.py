import unittest
import unittest.mock
import url as urlm
import itertools
import random
import string
import itertools
import logging
import os.path
import tempfile


RANDOM_STRING_LEN=64
TEMP_FILE_SIZE=1024


def setUpModule():
    """Disable logging while doing these tests."""
    logging.disable()


def tearDownModule():
    """Re-enable logging after doing these tests."""
    logging.disable(logging.NOTSET)


def random_string(size=RANDOM_STRING_LEN, chars=string.ascii_letters):
    """Generate a random string of SIZE using CHARS."""

    return ''.join(random.choices(chars, k=size))


def builtin_exceptions():
    """Generate builtin exception classes."""

    for exception in (x for x in dir(__builtins__) if x.endswith('Error')):
        yield eval(exception)


def random_file():
    """Create a temporary file with random contents and return its path."""

    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(os.urandom(TEMP_FILE_SIZE))

    return f.name


def urls_for_test():
    """URL generator."""

    protocols = ['', 'file:///', 'ftp://', 'http://', 'https://']
    paths = ['', 'home', 'home/foo', 'home/foo/bar.txt']
    params = ['', '?abc=cde', '?abc=cde&FgH=iJk!@#$%']
    randoms = ['', random_string()]

    for comb in itertools.product(protocols, paths, params, randoms):
        yield ''.join(comb)


class TestUrlInit(unittest.TestCase):
    """Url instantiation."""

    def test_exception_if_url_not_string(self):
        """Error when instantiated with something other than string."""

        for typer in (int, float, tuple, list, set, dict):
            with self.subTest(typer=typer):
                # Create a dummy object for test by calling each type.
                # Called without any arguments, ‘typer’ returns an object of
                # its type.
                with self.assertRaises(TypeError):
                    urlm.Url(typer())


    def test_no_exception_if_url_string(self):
        """No error when instantiated with string."""

        try:
            urlm.Url(str())
        except TypeError:
            self.fail('Raised TypeError when instantiated with string')


    def test_preserves_url(self):
        """Instantiation with URL honor received value."""

        for url in urls_for_test():
            with self.subTest(url=url):
                self.assertEqual(url, urlm.Url(url).url)


class TestAttr_responseurl(unittest.TestCase):
    """‘_responseurl’ attribute works properly."""

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


class TestAttr_urlpath(unittest.TestCase):
    """‘_urlpath’ attribute works properly."""

    def test_uses_expected_method(self):
        """Uses ‘urllib.parse.urlparse’, with the correct URL.

        It’s assumed that ‘urllib.parse.urlparse’ will be used."""

        with unittest.mock.patch('urllib.parse.urlparse') as urlparse_mock:
            # Get a test Url instance ready.
            url_obj = urlm.Url(random_string())

            # Using another random string for the attribute ‘_responseurl’ to
            # have an independent test that the program sets and gets it
            # properly, and that it does not change it before using it to
            # obtain ‘_urlpath’.
            responseurl = random_string()
            url_obj._responseurl = responseurl

            # Get the mocked method ready to be called.
            # Assigns the property ‘path’ to whatever is returned after calling
            # ‘urlparse_mock()’.
            # This is necessary because the parsed URL itself corresponds to the
            # property ‘path’ from the object that is returned from the parsing
            # method.
            urlparse_mock().path = random_string()

            # Force test object to parse its URL, giving it a reason to call
            # ‘urllib.parse.urlparse’.
            urlpath = url_obj._urlpath

            # Check if ‘urllib.parse.urlparse’ was called, and with the correct
            # URL.
            urlparse_mock.assert_called_with(responseurl)

            # Check if it assigned its attribute to the correct property from
            # the return value of ‘urllib.parse.urlparse’.
            self.assertEqual(url_obj._urlpath, urlparse_mock().path)


    def test_raises_errors(self):
        """Raises errors as promised in the docstring."""

        with unittest.mock.patch('urllib.parse.urlparse') as urlparse_mock:
            # Create a test object.
            url_obj = urlm.Url(random_string())
            url_obj._responseurl = random_string()

            # Make the mocked method raises the proper error when called.
            for exception in builtin_exceptions():
                # Skip more tricky Unicode exceptions for this test.
                if exception.__name__.startswith('Unicode'):
                    continue

                with self.subTest(exception=exception):
                    urlparse_mock.side_effect = exception

                    # Check if the expected error was raised as a result.
                    # For this, it suffices to get the attribute, which will
                    # then call ‘urllib.parse.urlparse’.
                    # ValueError should raise a RuntimeError.
                    # All other exceptions should raise themselves.
                    if exception is ValueError:
                        should_raise = RuntimeError
                    else:
                        should_raise = exception

                    with self.assertRaises(should_raise):
                        url_obj._urlpath


class TestAtrr_basename(unittest.TestCase):
    """‘_basename’ attribute works properly.

    It’s assumed that ‘os.path.basename’ will be used.

    Here we make sure that the program obtains the basename calling a trusted
    method with the correct argument (the previously parsed URL).
    Finally, we make sure that it assigns the exact return value of this method
    to the corresponding object’s attribute (that will be ultimately returned
    to the caller)."""

    def setUp(self):
        """Prepare an object for test"""

        self.url_obj = urlm.Url(random_string())
        self.url_obj._responseurl = random_string()


    def test_uses__urlpath(self):
        """Uses the proper method argument and honor its return value.

        The argument in this case is the attribute ‘_urlpath’, and the return
        value should be assigned to the attribute ‘_basename’."""

        with unittest.mock.patch('os.path.basename') as basename_mock:
            # Prepare the mock method’s return value.
            basename_mock.return_value = random_string()

            # The attribute being tested doesn’t have a setter, so it must be
            # accessed beforehand to force its value to be set.
            # This will also generate the call to ‘os.path.basename’, which is
            # being tested.
            self.url_obj._basename

            # Check if the proper argument was used to call the method.
            basename_mock.assert_called_with(self.url_obj._urlpath)

            # Check if the returned value was properly assigned.
            self.assertEqual(self.url_obj._basename,
                             basename_mock.return_value)


    def test_raises_errors(self):
        """Raises errors as promised in the docstring."""

        with unittest.mock.patch('os.path.basename') as basename_mock:
            # Make the mocked method raises the proper error when called.
            for exception in builtin_exceptions():
                # Skip more tricky Unicode exceptions for this test.
                if exception.__name__.startswith('Unicode'):
                    continue

                with self.subTest(exception=exception):
                    basename_mock.side_effect = exception

                    # Check if the expected error was raised as a result.
                    # For this, it suffices to get the attribute, which will
                    # then call ‘os.path.basename’.
                    with self.assertRaises(exception):
                        self.url_obj._basename


if __name__ == '__main__':
    unittest.main()
