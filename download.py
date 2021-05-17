import urllib.request
import urllib.parse
import urllib.error
import os
import tempfile
import shutil
import logging as log


error_msg = 'Error: {}'


class Url:
    """URL resources."""

    def __init__(self, url):
        """Use URL for the new instantiated object."""

        self.url = url


    @property
    def basename(self):
        """URL’s filename on the remote server.

        This is the “original” filename on the server from where it
        is being downloaded.
        It is obtained from the URL’s path, which may be different
        from the URL itself, in which case it must be parsed first.
        If this is the case, updates the URL path after parsing
        it."""

        if self.urlpath is None:
            try:
                self.urlpath = urllib.parse.urlparse(self.url).path
            except RuntimeError from ValueError:
                log.error('Malformed URL')
                raise
            except:
                log.error('Problems parsing URL')
                raise

        return os.path.basename(self.urlpath)


    def download(self, url=self.url, filename=None, tempfile=False):
        """Fetch and persist a file from a URL.

        Return the path where the file was saved to.
        If FILENAME was provided, use it; if not, use the name obtained from the remote server.
        When TEMPFILE is True, create a temporary"""

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
