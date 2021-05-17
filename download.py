import urllib.request
import urllib.parse
import urllib.error
import os
import tempfile
import shutil


error_msg = 'Error: {}'


class Url:
    """URL resources."""

    def __init__(self, url):
        """Use URL for the new instantiated object."""

        self.url = url


    def download(self, filename=None, tempfile=False):
        """Fetch and persist the file from the object’s URL.

        Return the path where the file was saved to.
        If FILENAME was provided, use it to save the file, or else
        use the name obtained from the remote server.
        When TEMPFILE is True, create a temporary"""

        try:
            with urllib.request.urlopen(url) as response:
                try:
                    parsed_url_path = urllib.parse.urlparse(response.url).path
                except:
                    print(error_msg.format('Problems parsing the URL'))
                    raise
                remote_filename = os.path.basename(parsed_url_path)
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
