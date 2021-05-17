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

    _responseurl = None
    _urlpath = None
    _basename = None


    def __init__(self, url):
        """Use URL for the new instantiated object."""

        self.url = url


    @property
    def responseurl(self):
        """Return of ‘urllib.request.urlopen(URL)’."""

        if not self._responseurl:
            err_msg = 'Response URL must be set first'
            log.error(err_msg)
            raise RuntimeError(err_msg)


    @property
    def urlpath(self):
        """Result of parsing the object’s URL.

        It is obtained from the URL’s path, which may be different
        from the URL itself in some cases."""

        if not self._urlpath:
            try:
                self._urlpath = urllib.parse.urlparse(self.url).path
            except RuntimeError from ValueError:
                log.error('Malformed URL')
                raise
            except:
                log.error('Problems parsing URL')
                raise

        return self._urlpath


    @property
    def basename(self):
        """URL’s filename on the remote server.

        “Original” filename on the server from where it is being
        accessed."""

        if self._basename is None:
            try:
                self._basename = os.path.basename(self.urlpath)
            except RuntimeError from Exception:
                log.error('Problems determining the basename')
                raise

        return self._basename


    def download(self):
        """Fetch file from URL and persist it locally as a temporary file.

        Returns the temporary filename."""

        try:
            with urllib.request.urlopen(url) as response:
                with tempfile.NamedTemporaryFile(delete=False) as f:
                    shutil.copyfileobj(response, f)
                local_filepath = f.name
        except ValueError:
            # Raised by urllib.request.urlopen or urllib.parse.urlparse.
            print(error_msg.format('Malformed or invalid URL'))
            # raise
        except urllib.error.URLError as e:
            # Raised by urllib.request.urlopen.
            print(error_msg.format(e.reason.strerror))
            # raise
        except:
            raise Exception('Error: download_temp: Download process failed')
        else:
            return local_filepath, remote_filename


download_temp('https://www.bits4wuts.com/foo.txt')
download_temp('')
download_temp('https://github.com/bits4waves/100daysofpractice-dataset/raw/master/requirements.txt')
