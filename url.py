# -*- coding: utf-8 -*-

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
    """URL download and remote filename retrieval."""

    __responseurl = None
    __urlpath = None
    __basename = None


    def __init__(self, url):
        """Use URL for the new instantiated object."""

        if type(url) is not str:
            raise TypeError('URL must be a string')

        self.url = url


    @property
    def _responseurl(self):
        """Return of ‘urllib.request.urlopen(URL)’.

        This property must be set before it can be accessed.
        This can be done with:

        with urllib.request.urlopen(self.url) as response:

            <...>

            self._responseurl = response.url

            <...>

        Raises RuntimeError if trying to access it when it is not
        set."""

        if self.__responseurl is None:
            err_msg = 'Response URL must be set first'
            log.error(err_msg)
            raise RuntimeError(err_msg)

        return self.__responseurl


    @_responseurl.setter
    def _responseurl(self, value):
        self.__responseurl = value


    @property
    def _urlpath(self):
        """Result of parsing the object’s URL.

        It is obtained from the URL’s path, which may be different
        from the URL itself in some cases.

        Raises RuntimeError if URL is malformed.
        Raises unexpected errors."""

        if not self.__urlpath:
            try:
                self.__urlpath = \
                    urllib.parse.urlparse(self._responseurl).path
            except ValueError as e:
                msg = 'Malformed URL'
                log.error(msg)
                raise RuntimeError(msg) from e
            except:
                msg = 'Unexpected error: {}'.format(sys.exc_info()[0])
                log.error(msg)
                raise

        return self.__urlpath


    @property
    def _basename(self):
        """URL’s filename on the remote server.

        “Original” filename on the server from where it is being
        accessed.

        Raises any errors that occur."""

        if not self.__basename:
            try:
                self.__basename = os.path.basename(self._urlpath)
            except:
                msg = 'Unexpected error: {}'.format(sys.exc_info()[0])
                log.error(msg)
                raise

        return self.__basename


    def download(self):
        """Fetch file from URL and persist it locally as a temporary file.

        Returns the temporary filename and the original filename on the
        server.

        Raises RuntimeError if the URL is malformed or if there were
        problems accessing it."""

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
            msg = 'Problems accessing URL: {}'.format(str(e))
            log.error(msg)
            raise RuntimeError(msg) from e
        except:
            msg = 'Unexpected error: {}'.format(sys.exc_info()[0])
            log.error(msg)
            raise
        else:
            return temp_f.name, self._basename


    def drive_it(url, credentials):
        """Saves the file from URL to Google Drive using CREDENTIALS."""

        pass
