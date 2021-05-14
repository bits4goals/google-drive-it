import shutil
import urllib.parse
import urllib.request
import os


def download_temp(url):
    """Download URL target, save it locally as a temporary file.
Return a tuple containing the local path where it was saved and its
remote original file name."""
    with urllib.request.urlopen(url) as response:
        parsed_url_path = urllib.parse.urlparse(response.url).path
        remote_filename = os.path.basename(parsed_url_path)
        with tempfile.NamedTemporaryFile(delete=False) as f:
            shutil.copyfileobj(response, f)
        local_filepath = f.name
    return (local_filepath, remote_filename)
