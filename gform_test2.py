# from datetime import datetime, timedelta
# delta = 5
# get_after = datetime.utcnow() - timedelta(minutes=delta)
# print(get_after.strftime('%Y-%m-%dT%H:%M:%SZ'))
test_response = {
  'responses': [
    {
      'responseId': 'ACYDBNhpYkZWRN2azCoqIaGZZcqE75i1SJJLUGkbTUUup2cUnoEHCXKeLVEk8lRKRD1TIJM',
      'createTime': '2023-05-07T23:00:02.695Z',
      'lastSubmittedTime': '2023-05-07T23:00:02.695614Z',
      'answers': {
        '1ed9e6f1': {
          'questionId': '1ed9e6f1',
          'textAnswers': {
            'answers': [
              {
                'value': 'pla'
              }
            ]
          }
        },
        '7f367d19': {
          'questionId': '7f367d19',
          'textAnswers': {
            'answers': [
              {
                'value': 'Zijue Chen'
              }
            ]
          }
        },
        '209a916b': {
          'questionId': '209a916b',
          'textAnswers': {
            'answers': [
              {
                'value': '2023-05-08 08:00'
              }
            ]
          }
        },
        '5ab11795': {
          'questionId': '5ab11795',
          'textAnswers': {
            'answers': [
              {
                'value': '2023-05-08 08:50'
              }
            ]
          }
        },
        '546904cb': {
          'questionId': '546904cb',
          'textAnswers': {
            'answers': [
              {
                'value': 'red'
              }
            ]
          }
        },
        '7b0a6168': {
          'questionId': '7b0a6168',
          'textAnswers': {
            'answers': [
              {
                'value': 'Under Extrusion'
              },
              {
                'value': 'Over Extrusion'
              },
              {
                'value': 'Warping'
              },
              {
                'value': 'G-Code related failure'
              },
              {
                'value': 'Filament ran out'
              },
              {
                'value': 'another potential issue'
              }
            ]
          }
        },
        '24ecbbd3': {
          'questionId': '24ecbbd3',
          'textAnswers': {
            'answers': [
              {
                'value': 'Bambu Lab P1P 2'
              }
            ]
          }
        }
      }
    }
  ]
}


# 1ed9e6f1: Material
# 7f367d19: Name
# 209a916b: Start Time
# 5ab11795: End Time
# 546904cb: Colour
# 7b0a6168: Issues
# 24ecbbd3: Printer
# 3486a80b: GCode
# 7eb791ce: STL


def get_text_answer(answers, question_id):
    return answers[question_id]['textAnswers']['answers'][0]['value']


if __name__ == '__main__':
    for response in test_response['responses']:
        print(f"{response['responseId']} created at {response['createTime']}")
        print(f"{response['answers']['7b0a6168']['textAnswers']['answers']}")
        # for issue in response['answers']['7b0a6168']['textAnswers']['answers']:
        #     print(issue['value'])

        thing = [issue['value'] for issue in response['answers']['7b0a6168']['textAnswers']['answers']]
        print(thing)
        # resp_id_to_add = response['responseId']
        # for question_id in response['answers'].keys():
        #     print(question_id)
            # match question_id:
            #     case '7f367d19': # Name
            #         data_to_add['owner_name'] = get_text_answer(response['answers'], question_id)
            #     case '24ecbbd3': # Printer
            #         data_to_add['printer'] = get_text_answer(response['answers'], question_id)
            #     case '209a916b': # Start Time
            #         data_to_add['start_time'] = get_text_answer(response['answers'], question_id)
            #     case '5ab11795': # End Time:
