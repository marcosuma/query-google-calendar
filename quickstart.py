from __future__ import print_function

# import datetime
import os.path
from datetime import datetime
import pytz

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def main():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        text_query = input('Please enter your text query input: ')
        timezone = input(
            'In which timezone you want it (e.g. Europe/London) - by default it\'s your current calendar timezone: ')

        # Call the Calendar API
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time

        page_token = None
        while True:
            # calls the Calendar API
            events_result = service.events().list(calendarId='primary', timeMin=now,
                                                  maxResults=50, singleEvents=True,
                                                  orderBy='startTime', q=text_query).execute()

            # parses the response
            events = events_result.get('items', [])
            if not events:
                print('No upcoming events found.')
                return

            # timezones = ['America/Los_Angeles', 'Europe/Madrid', 'Europe/London', 'Asia/Singapore']
            # prints the events
            for event in events:
                start = event['start'].get(
                    'dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                # all_times = []
                # for tz in timezones:
                #     local_datetime = datetime_start_orig.astimezone(pytz.timezone(tz))
                #     all_times.append(local_datetime)
                if timezone != "":
                    localFormat = "%Y-%m-%dT%H:%M:%S%z"
                    datetime_start_orig = datetime.strptime(start, localFormat)
                    local_start = datetime_start_orig.astimezone(
                        pytz.timezone(timezone))
                    local_start = local_start.strftime("%a, %d %b, %Y %H:%M")
                if timezone != "":
                    localFormat = "%Y-%m-%dT%H:%M:%S%z"
                    datetime_end_orig = datetime.strptime(end, localFormat)
                    local_end = datetime_end_orig.astimezone(
                        pytz.timezone(timezone))
                    local_end = local_end.strftime("%H:%M")

                print(local_start if local_start != None else start, "-",
                      local_end if local_end != None else end)

            # check if next page is available.
            page_token = events_result.get('nextPageToken')
            if not page_token:
                break

    except HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    main()
