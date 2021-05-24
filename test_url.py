import unittest
import unittest.mock
import url as urlm
import itertools
import random
import string
import itertools
import logging
import os
import os.path
from tempfile import NamedTemporaryFile, gettempdir
import filecmp
import urllib


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


def random_temp_file():
    """Create a temporary file with random binary content.  Return its path."""

    with NamedTemporaryFile(delete=False) as f:
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
                # Skip trickier Unicode exceptions.
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
                # Skip trickier Unicode exceptions.
                if exception.__name__.startswith('Unicode'):
                    continue

                with self.subTest(exception=exception):
                    basename_mock.side_effect = exception

                    # Check if the expected error was raised as a result.
                    # For this, it suffices to get the attribute, which will
                    # then call ‘os.path.basename’.
                    with self.assertRaises(exception):
                        self.url_obj._basename


class TestDownload(unittest.TestCase):
    """Correctly obtains and persists URL’s file."""

    def setUp(self):
        """Create test file to be downloaded and test object to do it."""

        self.f_remote = random_temp_file()

        self.url_obj = urlm.Url(random_string())
        self.url_obj._responseurl = random_string()


    def tearDown(self):
        """Remove the temporary test file."""

        os.remove(self.f_remote)


    def test_download(self):
        """Fetches and persists file from URL and returns filenames.

        The filenames are the original remote name of the file and the name
        used to save it after the download."""

        with open(self.f_remote, 'w+b') as f:
            with unittest.mock.patch('urllib.request.urlopen') as urlopen_mock:
                # Use the local random temporary file to mock a remote file
                # to be downloaded.
                urlopen_mock.return_value = f

                # Use a mock for the attribute ‘_basename’ to avoid having to
                # mock both ‘os.path.basename’ and ‘urllib.parse.urlparse’.
                with unittest.mock.patch('url.Url._basename',
                                     new_callable=unittest.mock.PropertyMock) \
                                 as _basename_mock:
                    _basename_test = random_string()
                    _basename_mock.return_value = _basename_test

                    # This mock is necessary as the property is accessed inside
                    # the method ‘download()’ being tested.
                    urlopen_mock().url = ''

                    f_downloaded, f__basename = self.url_obj.download()

        # Check if it was saved in the temporary directory.
        self.assertEqual(os.path.dirname(f_downloaded), gettempdir())

        # Check the integrity of the dowloaded file.
        self.assertTrue(filecmp.cmp(f_downloaded, self.f_remote))

        # Check if it returned the correct basename of the remote file.
        self.assertEqual(f__basename, _basename_test)

        os.remove(f_downloaded)


    def test_raises_errors(self):
        """Raises exceptions as promised in the docstring"""

        with unittest.mock.patch('urllib.request.urlopen') as urlopen_mock:
            exceptions = list(builtin_exceptions())
            URLError = urllib.error.URLError
            exceptions.append(URLError)
            for exception in exceptions:
                # Skip trickier Unicode exceptions.
                if exception.__name__.startswith('Unicode'):
                    continue

                # Raises RuntimeError when ValueError or urllib.error.URLError
                # were raised, which are triggered by a malformed URL or if
                # there were problems accessing it, respectively.
                # Raises the exception itself for all others.
                with self.subTest(exception=exception):
                    urlopen_mock.side_effect = exception
                    if exception is ValueError:
                        expected_exception = RuntimeError
                    elif exception is urllib.error.URLError:
                        # This exception must be initialized with an argument
                        # that has the property ‘strerror’ (‘OSError’ does).
                        urlopen_mock.side_effect = exception(OSError)
                        expected_exception = RuntimeError
                    else:
                        expected_exception = exception

                    with self.assertRaises(expected_exception):
                        self.url_obj.download()


class TestChunk(unittest.TestCase):
    """Correctly chunk file."""

    def test_chunk(self):
        """Copy file per chunks and test for equality."""

        # Just a helper function to make things clearer.
        get_chunk = urlm.Url.chunk

        # Create the test file whose data will be copied.
        original_fname = random_temp_file()
        with open(original_fname, 'rb') as original:
            # Create an empty test file to receive the copied data.
            # delete=False is important to prevent it being deleted
            # at the end of the with, so the file comparison for the
            # assertion test will be possible.
            with NamedTemporaryFile('wb', delete=False) as copy:
                # Initilize the position of the first byte to be
                # copied.
                first = 0
                # Get the total file size in bytes.
                file_size = os.fstat(original.fileno()).st_size
                # Test with different chunk sizes.
                for chunk_size in [1, 2, 3, 5, 7, 11, 256]:
                    with self.subTest(chunk_size=chunk_size):
                        # Copy the file in chunks, update the value
                        # of the next first byte to be copied.
                        while first < file_size:
                            chunk = get_chunk(original, first,
                                              chunk_size)
                            copy.write(chunk)
                            first += chunk_size

        # check if copy was successful
        self.assertTrue(filecmp.cmp(copy.name, original_fname))

        os.remove(original_fname)
        os.remove(copy.name)


if __name__ == '__main__':
    unittest.main()
