import pydrive
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import oauth as oa


def main():
    gauth = GoogleAuth()
    while True:
        try:
            # Creates local webserver and attempts authentication.
            gauth.LocalWebserverAuth()
        except pydrive.settings.InvalidConfigError:
            # File ‘client_secrets.json’ is not present.
            id, secret = oa.get_id_secret()
            if id and secret:
                oa.create_settings_file(id, secret)

    drive = GoogleDrive(gauth)

    file1 = drive.CreateFile({'title': 'Hello.txt'})  # Create GoogleDriveFile instance with title 'Hello.txt'.
    file1.SetContentString('Hello World!') # Set content of the file from given string.
    file1.Upload()

if __name__ == '__main__':
    main()
