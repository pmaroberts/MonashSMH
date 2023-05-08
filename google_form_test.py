from __future__ import print_function

import os
import pickle
import time
from datetime import datetime, timedelta
from urllib.request import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from database import Database, CursorFromConnectionPool


def main():
    Database.initialise(database="gform_spike", user="postgres", password="1234", host='localhost')
    while True:
        time.sleep(5)
        result = get_fresh_form_responses()
        if len(result) > 0:
            for response in result['responses']:
                if not_duplicate(response['responseId']):
                    add_print_job_to_db(printer_name=get_text_answer(response['answers'], '24ecbbd3'),
                                        start_time=get_text_answer(response['answers'], '209a916b'),
                                        end_time=get_text_answer(response['answers'], '5ab11795'),
                                        colour=get_text_answer(response['answers'], '546904cb'),
                                        material=get_text_answer(response['answers'], '1ed9e6f1'),
                                        response_code=response['responseId'],
                                        owner_name=get_text_answer(response['answers'], '7f367d19'),
                                        issues=[issue['value'] for issue in
                                                response['answers']['7b0a6168']['textAnswers']['answers']])

    # with open('test_output.json', 'w') as f:
    #     f.write(str(result))
    # for response in result:
    #     resp_id = response['responseId']
    #     resp_time = response['createTime']
    #     resp_value = response['answers']['54519c7c']['textAnswers']['answers'][0]['value']
    #     print(f"We got back {resp_id} at {resp_time} with value {resp_value}")
    #     add_to_db(resp_value)


def add_to_db(some_text: str):
    with CursorFromConnectionPool() as cursor:
        cursor.execute(f"INSERT INTO testing_table(some_text) VALUES ('{some_text}');")


def not_duplicate(response_id: str):
    with CursorFromConnectionPool() as cursor:
        cursor.execute(f"""SELECT print_id FROM "PRINT_PART" WHERE UPPER(form_code) = UPPER('{response_id}')""")
        if len(cursor.fetchall()) != 0:
            cursor.__exit__(None, None, None)
            print("can't add, dupe")
            return False
    return True


def add_print_job_to_db(printer_name, start_time, end_time, colour, material, response_code, owner_name, issues):
    with CursorFromConnectionPool() as cursor:
        cursor.execute(f"""
                                 insert into "PRINT_PART" values (DEFAULT,
                                 (select printer_id from "PRINTER" where UPPER(printer_name) = UPPER('{printer_name}')),
                                 to_timestamp('{start_time}', 'yyyy-mm-dd hh24:mi'),
                                 to_timestamp('{end_time}', 'yyyy-mm-dd hh24:mi'),
                                 '{colour}',
                                 '{material}',
                                 '{response_code}',
                                 (select owner_id from "PRINT_OWNER" where UPPER(owner_name) = UPPER('{owner_name}'))
                                 );
                        """)
        for issue in issues:
            cursor.execute(f"""
                                insert into "PRINT_ISSUE" values (
                                (select print_id from "PRINT_PART" where UPPER(form_code) = UPPER('{response_code}')),
                                '{issue}');
                            """)


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
    form_id = '1qSkZVknek-KATVkRSKV8agM6CqvROLK4v0dsXQ-zPsk'  # For the print logging form

    delta = 5
    get_after = datetime.utcnow() - timedelta(minutes=delta)
    result = service.forms().responses().list(formId=form_id,
                                              filter=f"timestamp > {get_after.strftime('%Y-%m-%dT%H:%M:%SZ')}").execute()
    print(result)
    return result


def get_text_answer(answers, question_id):
    return answers[question_id]['textAnswers']['answers'][0]['value']


if __name__ == '__main__':
    main()
