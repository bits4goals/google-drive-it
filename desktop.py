from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

TOKEN_FILE = 'token-desktop.json'
CLIENT_SECRETS_FILE = 'client_secrets-desktop.json'
SCOPES = ['https://www.googleapis.com/auth/drive.file']

credentials = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
# Note: this is *not* the credentials file.
if os.path.exists(TOKEN_FILE):
    credentials = Credentials.\
        from_authorized_user_file(TOKEN_FILE, SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not credentials or not credentials.valid:
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, SCOPES)
        credentials = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open(TOKEN_FILE, 'w') as token:
        token.write(credentials.to_json())
