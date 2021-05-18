import urllib.request
import urllib.parse
import urllib.error
import os
import tempfile
import shutil
import logging as log
import sys


error_msg = 'Error: {}'


class Url:
    """URL stuff."""

    __responseurl = None
    _urlpath = None
    _basename_f = None


    def __init__(self, url):
        """Use URL for the new instantiated object."""

        self.url = url


    @property
    def _responseurl(self):
        """Return of ‘urllib.request.urlopen(URL)’."""

        if not self.__responseurl:
            err_msg = 'Response URL must be set first'
            log.error(err_msg)
            raise RuntimeError(err_msg)

        return self.__responseurl


    @_responseurl.setter
    def _responseurl(self, value):
        self.__responseurl = value


    @property
    def urlpath(self):
        """Result of parsing the object’s URL.

        It is obtained from the URL’s path, which may be different
        from the URL itself in some cases."""

        if not self._urlpath:
            try:
                self._urlpath = \
                    urllib.parse.urlparse(self._responseurl).path
            except ValueError as e:
                msg = 'Malformed URL'
                log.error(msg)
                raise RuntimeError(msg) from e
            except:
                msg = 'Unexpected error: {}'.format(sys.exc_info()[0])
                log.error(msg)
                raise

        return self._urlpath


    @property
    def basename_f(self):
        """URL’s filename on the remote server.

        “Original” filename on the server from where it is being
        accessed."""

        if not self._basename_f:
            try:
                self._basename_f = os.path.basename(self.urlpath)
            except:
                msg = 'Unexpected error: {}'.format(sys.exc_info()[0])
                log.error(msg)
                raise

        return self._basename_f


    def download(self):
        """Fetch file from URL and persist it locally as a temporary file.

        Returns the temporary filename and the original filename on the
        server."""

        try:
            with urllib.request.urlopen(self.url) as response:
                with tempfile.NamedTemporaryFile(delete=False) as temp_f:
                    shutil.copyfileobj(response, temp_f)

                # Set property in the appropriate context, while we
                # still have access to the data.
                self._responseurl = response.url
        except ValueError as e:
            msg = 'Malformed or invalid URL'
            log.error(msg)
            raise RuntimeError(msg) from e
        except urllib.error.URLError as e:
            msg = 'Problems accessing URL: {}'.format(e.reason.strerror)
            log.error(msg)
            raise RuntimeError(msg) from e
        except:
            msg = 'Unexpected error: {}'.format(sys.exc_info()[0])
            log.error(msg)
            raise
        else:
            return temp_f.name, self.basename_f


# download_temp('https://www.bits4wuts.com/foo.txt')
# download_temp('')
# download_temp('https://github.com/bits4waves/100daysofpractice-dataset/raw/master/requirements.txt')
my_url = Url('https://github.com/bits4waves/100daysofpractice-dataset/raw/master/requirements.txt')
result = my_url.download()
