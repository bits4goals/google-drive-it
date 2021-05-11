import os


FILENAME = "settings.yaml"

def create_settings_file(id, secret):
    """Create settings file for client ID and SECRET.

Use the recommended settings for silent authentication on a remote
machine.
See: https://googleworkspace.github.io/PyDrive/docs/build/html/oauth.html#automatic-and-custom-authentication-with-settings-yaml"""

    content = """
client_config_backend: settings
client_config:
  client_id: {}
  client_secret: {}
save_credentials: True
save_credentials_backend: file
save_credentials_file: credentials.json

get_refresh_token: True

oauth_scope:
  - https://www.googleapis.com/auth/drive.file
  - https://www.googleapis.com/auth/drive.install
"""

    with open(FILENAME, "w") as f:
        f.write(content.format(id, secret))

def get_id_secret_from_env():
    """Try to fetch id and secret from environment variables."""
    id = os.getenv('GOOGLE_DRIVE_OAUTH_ID')
    secret = os.getenv('GOOGLE_DRIVE_OAUTH_SECRET')
    return (id, secret) if id and secret else (None, None)

def get_id_secret_from_user():
    print("Please inform the OAuth Credentials.")
    id = input("Client ID: ")
    secret = input("Client secret: ")
    return (id, secret) if id and secret else (None, None)

def get_id_secret():
    """Try to get id and secret from environment variables, the user input."""
    id, secret = get_id_secret_from_env()
    if not (id and secret):
        id, secret = get_id_secret_from_user()
    return (id, secret) if id and secret else (None, None)
