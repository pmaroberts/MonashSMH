from __future__ import print_function

import os
import pickle
from datetime import datetime, timedelta
from urllib.request import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from database import Database, CursorFromConnectionPool


def main():
    Database.initialise(database="gform_spike", user="postgres", password="1234", host='localhost')
    result = get_fresh_form_responses()
    for response in result:
        resp_id = response['responseId']
        resp_time = response['createTime']
        resp_value = response['answers']['54519c7c']['textAnswers']['answers'][0]['value']
        print(f"We got back {resp_id} at {resp_time} with value {resp_value}")
        add_to_db(resp_value)


def add_to_db(some_text: str):
    with CursorFromConnectionPool() as cursor:
        cursor.execute(f"INSERT INTO testing_table(some_text) VALUES ('{some_text}');")


def get_fresh_form_responses():
    # Currently updating for every 5 seconds
    SCOPES = "https://www.googleapis.com/auth/forms.responses.readonly"
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('forms', 'v1', credentials=creds)

    # Prints the responses of your specified form:
    form_id = '1S800EGRwYSvi93UWMXyBMb2ak5OsikJXt18uNK6AxrM'
    delta = 5
    get_after = datetime.utcnow() - timedelta(hours=delta)
    result = service.forms().responses().list(formId=form_id, filter=f"timestamp > {get_after.strftime('%Y-%m-%dT%H:%M:%SZ')}").execute()
    print(result)
    return result['responses']


if __name__ == '__main__':
    main()
