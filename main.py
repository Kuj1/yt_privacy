import json
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# API_KEY = ''

DATA_FOLDER = os.path.join(os.getcwd(), 'data_folder')
USER_FOLDER = os.path.join(os.getcwd(), 'user_folder')

VIDEOS_INFO = os.path.join(USER_FOLDER, 'videos_info.txt')
APP_TOKEN_FILE = os.path.join(DATA_FOLDER, 'client_secret.json')
USER_TOKEN_FILE = os.path.join(DATA_FOLDER, 'user_token.json')

SCOPES = [
    'https://www.googleapis.com/auth/youtube.force-ssl',
    'https://www.googleapis.com/auth/userinfo.profile',
]


def compile_videos_info():
    videos_info = list()
    with open(VIDEOS_INFO, 'r') as videos:
        for info in videos.readlines():
            url = info.split(" ")[0]
            time = info.split(" ")[1]
            videos_info.append(
                {
                    'id': f'{url.split("=")[1].strip()}',
                    'time': time.replace('\n', '').strip()
                }
            )
    return videos_info


# Reusable user OAuth2 token
def get_creds_saved():
    creds = None

    if os.path.exists(USER_TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(USER_TOKEN_FILE, SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(USER_TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return creds


# Get YouTube API service
def get_service():
    creds = get_creds_saved()
    service = build('oauth2', 'v2', credentials=creds)
    return service


# Get User Info
def get_user_info():
    response_user_info = get_service().userinfo().get().execute()
    print(f'{"-" * 12}Account Info{"-" * 12}')
    print(f'Name account: {json.dumps(response_user_info["name"])}\n'
          f'Id account: {json.dumps(response_user_info["id"])}')


# Set privacy to your videos
def set_privacy(info):
    creds = get_creds_saved()
    youtube = build('youtube', 'v3', credentials=creds)
    for first_l in info:
        request = youtube.videos().update(
            part="id, status",
            body={
                "id": f"{first_l['id']}",
                "status": {
                    "privacyStatus": "private",
                    "publishAt": f"2023-02-23T{first_l['time']}:00.00+03:00",
                }
            }
        )

        response_video_info = request.execute()
        print(f'{"-"*12}Video Info{"-"*12}')
        print(f'video url: https://www.youtube.com/watch?v={response_video_info["id"]}\n'
              f'Publish at (UTC+3): {response_video_info["status"]["publishAt"]}')


if __name__ == '__main__':
    get_user_info()
    set_privacy(info=compile_videos_info())
    os.remove(os.path.join(DATA_FOLDER, 'user_token.json'))
