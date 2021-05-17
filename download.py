import urllib.request
import urllib.parse
import urllib.error
import os
import tempfile
import shutil
import logging as log


error_msg = 'Error: {}'


class Url:
    """URL stuff."""

    __responseurl = None
    __urlpath = None
    __basename = None


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


    @property
    def _urlpath(self):
        """Result of parsing the object’s URL.

        It is obtained from the URL’s path, which may be different
        from the URL itself in some cases."""

        if not self.__urlpath:
            try:
                self.__urlpath = urllib.parse.urlparse(self._responseurl).path
            except RuntimeError from ValueError:
                log.error('Malformed URL')
                raise
            except:
                log.error('Problems parsing URL')
                raise

        return self.__urlpath


    @property
    def _basename(self):
        """URL’s filename on the remote server.

        “Original” filename on the server from where it is being
        accessed."""

        if self.__basename is None:
            try:
                self.__basename = os.path.basename(self._urlpath)
            except e:
                msg = 'Problems determining the basename'
                log.error(msg)
                raise RuntimeError(msg) from e

        return self.__basename


    def download(self):
        """Fetch file from URL and persist it locally as a temporary file.

        Returns the temporary filename and the original filename on the
        server."""

        try:
            with urllib.request.urlopen(url) as response:
                with tempfile.NamedTemporaryFile(delete=False) as f:
                    shutil.copyfileobj(response, f)
                temp_filename = f.name

                # Set property in the appropriate context, while we
                # still have access to the data.
                self.__responseurl = response.url
        except ValueError:
            print(error_msg.format('Malformed or invalid URL'))
            raise
        except urllib.error.URLError as e:
            print(error_msg.format(e.reason.strerror))
            raise
        except e:
            msg = 'Problems downloaing the file'
            log.error(msg)
            raise RuntimeError(msg) from e
        else:
            return local_filepath, temp_filename


download_temp('https://www.bits4wuts.com/foo.txt')
download_temp('')
download_temp('https://github.com/bits4waves/100daysofpractice-dataset/raw/master/requirements.txt')
