# -*- coding: utf-8 -*-

import urllib.request
import urllib.parse
import urllib.error
import os
import tempfile
import shutil
import logging as log
import sys
import requests


error_msg = 'Error: {}'

# The documentation suggests using a multiple of 256 kB for the
# multipart upload.  The default here will be 512 kB.
# https://developers.google.com/drive/api/v3/manage-uploads#uploading
DEFAULT_CHUNK_SIZE = 2 * 256 * 1024

class Url:
    """URL download and remote filename retrieval."""

    __responseurl = None
    __urlpath = None
    __basename = None
    _filename = None


    def __init__(self, url, token):
        """Use URL and TOKEN for the new instantiated object."""

        for param, name in ((url, 'URL'), (token, 'Token')):
            if type(param) is not str:
                raise TypeError('{} must be a string'.format(param))

        self.url = url
        self.token = token


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


    @property
    def filename(self):
        """Local name of the downloaded file."""

        if self._filename is None:
            raise RuntimeError('File name is not set')

        return self._filename


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
                    self._filename = temp_f.name

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
            return self.filename, self._basename


    @staticmethod
    def get_chunk(f, first_byte, chunk_size=DEFAULT_CHUNK_SIZE):
        """Return contiguous bytes from a file."""

        f.seek(first_byte)
        return f.read(chunk_size)


    def _get_upload_url(self):
        """Fetch POST address from API."""

        # The file will be uploaded via a POST request.
        # First, the initial request will be sent with the OAuth token.
        # If the initial request succeeds, the API will return the URL to be used
        # for the upload.
        # Here the configuration for the initial request is prepared.
        headers = {'Authorization': 'Bearer ' + self.token,
                             'Content-Type': 'application/json'}
        params = {'name': os.path.basename(self.filename)}

        # Send the initial request, obtaining:
        # status code: “200 OK” when it succeeds
        # location: when it succeeds, this is the URL to be used for the upload.
        request = requests.post(
            'https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable',
            headers=headers,
            data=json.dumps(params))

        if getattr(request, 'status_code') == 200:
            upload_url = request.headers['Location']
        else:
            raise RuntimeError('Problems obtaining upload URL from API')

        return upload_url


    def _get_upload_headers(first_byte, file_size,
                            chunk_size=DEFAULT_CHUNK_SIZE):
        """Prepare the string for the POST request's headers."""

        content_range = 'bytes ' + \
            str(first_byte) + \
            '-' + \
            str(first_byte + chunk_size - 1) + \
            '/' + \
            str(file_size)

        return {'Content-Range': content_range}


    @staticmethod
    def get_last_uploaded_byte(request):
        """Return last uploade byte.."""

        return int(request.headers['Range'].split('-')[-1])


    def _upload(self):
        """Upload the file to Google Drive using the OAuth token."""

        try:
            upload_url = _get_upload_url(self.token)

            # It will be done multiple HTTP requests.
            f = open(self.filename, 'rb')
            first_byte = 0
            file_size = os.path.getsize(self.filename)
            while first_byte < file_size:
                chunk = get_chunk(f, first_byte)

                # Prepare the headers for the upload request.
                headers = _get_upload_headers(first_byte, file_size)

                # Send the data chunk upload request.
                request = requests.put(upload_url,
                                       headers=headers,
                                       data=chunk)

                # A response with status code of 200 or 201 indicates
                # that the upload is complete.
                if getattr(request, 'status_code') in (200, 201):
                    break

                # The response will contain the last successfully
                # uploaded byte.  It may or may not differ from the
                # last byte of the chunk we just tried to upload.
                first_byte = get_last_uploaded_byte(request) + 1
        except RuntimeError:
            raise
        except:
            raise
        finally:
            try:
                f.close()
            except:
                pass


    def drive_it(self):
        """Save the file from URL to Google Drive."""

        try:
            self.download()
            self._upload()
        except RuntimeError as e:
            error = str(e)
