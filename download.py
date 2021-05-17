import shutil
import urllib.request
import urllib.parse
import urllib.error
import os


error_msg = 'Error: {}'


def download_temp(url):
    """Download URL target, save it locally as a temporary file.
Return a tuple containing the local path where it was saved and its
remote original file name.

Raises:
ValueError (malformed url)
URLError
"""
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
