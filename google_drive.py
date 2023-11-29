import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

import webbrowser    
urL='https://www.google.com'
chrome_path="C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
webbrowser.register('chrome', None,webbrowser.BackgroundBrowser(chrome_path))
webbrowser.get('chrome').open_new_tab(urL)

# If modifying these scopes, delete the file token.json.


def upload_file(filepath, creds):
    try:
        service = build("drive", "v3", credentials=creds)

        file_metadata = {
            'name': os.path.basename(filepath),
            'parents': ['1YqgyeqT0vlQL31AB1-RopXGIfJAhlyqZ']
        }

        media = MediaFileUpload(filepath,mimetype='video/mp4')
        (service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute())
        
        print("File uploaded successfully")
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f"An error occurred: {error}")

def create_folder(creds):
  """Create a folder and prints the folder ID
  Returns : Folder Id

  Load pre-authorized user credentials from the environment.
  TODO(developer) - See https://developers.google.com/identity
  for guides on implementing OAuth2 for the application.
  """

  try:
    # create drive api client
    service = build("drive", "v3", credentials=creds)
    file_metadata = {
        "name": "Invoices",
        "mimeType": "application/vnd.google-apps.folder",
    }

    # pylint: disable=maybe-no-member
    file = service.files().create(body=file_metadata, fields="id").execute()
    print(f'Folder ID: "{file.get("id")}".')
    return file.get("id")

  except HttpError as error:
    print(f"An error occurred: {error}")
    return None

def google_login():
    SCOPES = ["https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive.appdata", "https://www.googleapis.com/auth/drive.install", "https://www.googleapis.com/auth/drive"]
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(creds.to_json())
    return creds