# -*- coding: utf-8 -*-

import os
import flask
from flask import request
import requests

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

import json

import logging
import url as urlm

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/drive.file']
API_SERVICE_NAME = 'drive'
API_VERSION = 'v3'

app = flask.Flask(__name__)
# Note: A secret key is included in the sample so that it works.
# If you use this code in your application, replace this with a truly secret
# key. See https://flask.palletsprojects.com/quickstart/#sessions.
app.secret_key = 'REPLACE ME - this value is here as a placeholder.'


@app.route('/', methods=['GET', 'POST'])
def index():
  # Download file from the URL to a local temporary file.
  # tmp_filename: complete path to the downloaded file (random name,
  #   without extension)
  # remote_basename: filename with extension of the downloaded file as it was
  #   called on the remote server from which it was downloaded.
  if flask.request.method == 'POST':
    try:
      tmp_filename, remote_basename = urlm.Url(request.form['url']).download()
    except RuntimeError as e:
      error = str(e)

  # Instantiate the object with the OAuth credentials that will be used to
  # obtain upload access to the Google Drive.
  credentials = google.oauth2.credentials.\
    Credentials(**flask.session['credentials'])

  # The file will be uploaded via a POST request.
  # First, the initial request will be sent with the OAuth credentials.
  # If the initial request succeeds, the API will return the URL to be used
  # for the upload.
  # Here the configuration for the initial request is prepared.
  headers = {'Authorization': 'Bearer ' + credentials.token,
             'Content-Type': 'application/json'}
  params = {'name': os.path.basename(file_path)}

  # Send the initial request, obtaining:
  # status_code: “200 OK” when it succeeds
  # upload_url: when it succeeds, this is the URL to use for the upload.
  request = requests.post(
    'https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable',
    headers=headers,
    data=json.dumps(params))
  status_code = getattr(request, 'status_code')
  upload_url = request.headers['Location']

  return flask.render_template('index.html',
                               url=url,
                               local_filename=local_filename,
                               remote_basename=remote_basename,
                               error=error)


@app.route('/test')
def test_api_request():
  if 'credentials' not in flask.session:
    return flask.redirect('authorize')

  # Load credentials from the session.
  credentials = google.oauth2.credentials.Credentials(
      **flask.session['credentials'])

  drive = googleapiclient.discovery.build(
      API_SERVICE_NAME, API_VERSION, credentials=credentials)

  files = drive.files().list().execute()

  # Save credentials back to session in case access token was refreshed.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  flask.session['credentials'] = credentials_to_dict(credentials)

  return flask.jsonify(**files)


@app.route('/authorize')
def authorize():
  # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES)

  # The URI created here must exactly match one of the authorized redirect URIs
  # for the OAuth 2.0 client, which you configured in the API Console. If this
  # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
  # error.
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true')

  # Store the state so the callback can verify the auth server response.
  flask.session['state'] = state

  return flask.redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
  # Specify the state when creating the flow in the callback so that it can
  # verified in the authorization server response.
  state = flask.session['state']

  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  # Use the authorization server's response to fetch the OAuth 2.0 tokens.
  authorization_response = flask.request.url
  flow.fetch_token(authorization_response=authorization_response)

  # Store credentials in the session.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  credentials = flow.credentials
  flask.session['credentials'] = credentials_to_dict(credentials)

  return flask.redirect(flask.url_for('test_api_request'))


@app.route('/revoke')
def revoke():
  if 'credentials' not in flask.session:
    return ('You need to <a href="/authorize">authorize</a> before ' +
            'testing the code to revoke credentials.')

  credentials = google.oauth2.credentials.Credentials(
    **flask.session['credentials'])

  revoke = requests.post('https://oauth2.googleapis.com/revoke',
      params={'token': credentials.token},
      headers = {'content-type': 'application/x-www-form-urlencoded'})

  status_code = getattr(revoke, 'status_code')
  if status_code == 200:
    return('Credentials successfully revoked.' + print_index_table())
  else:
    return('An error occurred.' + print_index_table())


def get_chunks(file_object, chunk_size=512*1024):
  """Act as a generator, yielding file in chunks.
Chunk has a default size of 256k.
Source: https://stackoverflow.com/a/519653/3684790"""
  while True:
    data = file_object.read(chunk_size)
    if not data:
      break
    yield data


@app.route('/upload/<path:url>')
def upload(url):
  with open(file_path, 'rb') as f:
    file_size = str(os.path.getsize(file_path))
    current_byte = 0
    for chunk in get_chunks(f):
      content_range = 'bytes ' + \
        str(current_byte) + \
        '-' + \
        str(current_byte + len(chunk) - 1) + \
        '/' + \
        str(file_size)
      headers = {'Content-Range': content_range}

      request = requests.put(upload_url,
                             headers=headers,
                             data=chunk)

      response = getattr(request, 'status_code')
      if response in (200, 201):
        break

      print(content_range)
      print(upload_url)
      print(request)

      current_byte = int(request.headers['Range'].split('-')[-1]) + 1

  return f'status_code: {status_code}<br>upload_url: {upload_url}'


@app.route('/clear')
def clear_credentials():
  if 'credentials' in flask.session:
    del flask.session['credentials']
  return ('Credentials have been cleared.<br><br>' +
          print_index_table())


def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

def print_index_table():
  return ('<table>' +
          '<tr><td><a href="/test">Test an API request</a></td>' +
          '<td>Submit an API request and see a formatted JSON response. ' +
          '    Go through the authorization flow if there are no stored ' +
          '    credentials for the user.</td></tr>' +
          '<tr><td><a href="/authorize">Test the auth flow directly</a></td>' +
          '<td>Go directly to the authorization flow. If there are stored ' +
          '    credentials, you still might not be prompted to reauthorize ' +
          '    the application.</td></tr>' +
          '<tr><td><a href="/revoke">Revoke current credentials</a></td>' +
          '<td>Revoke the access token associated with the current user ' +
          '    session. After revoking credentials, if you go to the test ' +
          '    page, you should see an <code>invalid_grant</code> error.' +
          '</td></tr>' +
          '<tr><td><a href="/clear">Clear Flask session credentials</a></td>' +
          '<td>Clear the access token currently stored in the user session. ' +
          '    After clearing the token, if you <a href="/test">test the ' +
          '    API request</a> again, you should go back to the auth flow.' +
          '</td></tr></table>')


if __name__ == '__main__':
  # ‘localhost’ is a regular (empty) file used as a flag: if it is
  # present, run locally.
  if os.path.exists('localhost'):
    # When running locally, disable OAuthlib's HTTPs verification.
    # ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

  # Specify a hostname and port that are set as a valid redirect URI
  # for your API project in the Google API Console.
  app.run('localhost', 8080, debug=True)
