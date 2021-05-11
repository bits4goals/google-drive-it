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
