# from datetime import datetime, timedelta
# delta = 5
# get_after = datetime.utcnow() - timedelta(minutes=delta)
# print(get_after.strftime('%Y-%m-%dT%H:%M:%SZ'))
test_response = {
    'responses': [
        {
            'responseId': 'ACYDBNiz1U-CSNWEuu8nZNcYjSbtHt8Cl_YpBjX9Bp5w8BRTCJI6nK0zz_YcXwUM4qmndkg',
            'createTime': '2023-04-24T01:46:55.238Z',
            'lastSubmittedTime': '2023-04-24T01:46:55.238088Z',
            'answers': {
                '54519c7c': {
                    'questionId': '54519c7c',
                    'textAnswers': {
                        'answers': [
                            {
                                'value': '2'
                            }
                        ]
                    }
                }
            }
        },
        {
            'responseId': 'ACYDBNj_e53ztdnDnVbS4dmgAk9m9vCQPwvybaZzhufmtOXdMpksDyuKq1DRo-A1tViHifA',
            'createTime': '2023-04-24T01:47:02.038Z',
            'lastSubmittedTime': '2023-04-24T01:47:02.038910Z',
            'answers': {
                '54519c7c': {
                    'questionId': '54519c7c',
                    'textAnswers': {
                        'answers': [
                            {
                                'value': '4'
                            }
                        ]
                    }
                }
            }
        },
        {
            'responseId': 'ACYDBNj8xAA3Tny-ryW03nboZ9OOgN1jkvQJtyGOtmDANNMT9637j2uqO3ttWnylMwR-sfQ',
            'createTime': '2023-04-24T01:46:58.170Z',
            'lastSubmittedTime': '2023-04-24T01:46:58.170956Z',
            'answers': {
                '54519c7c': {
                    'questionId': '54519c7c',
                    'textAnswers': {
                        'answers': [
                            {
                                'value': '3'
                            }
                        ]
                    }
                }
            }
        },
        {
            'responseId': 'ACYDBNhU9LGQUkmEqiHDpXC2mANJ9uLdVAxKxqDj80_uYJ47DYB9Cb0dGK5q52TCPAKcecE',
            'createTime': '2023-04-24T01:46:51.931Z',
            'lastSubmittedTime': '2023-04-24T01:46:51.931779Z',
            'answers': {
                '54519c7c': {
                    'questionId': '54519c7c',
                    'textAnswers': {
                        'answers': [
                            {
                                'value': '1'
                            }
                        ]
                    }
                }
            }
        }
    ]
}

for response in test_response["responses"]:
    print(
        f"{response['responseId']} created at {response['createTime']} answer was {response['answers']['54519c7c']['textAnswers']['answers'][0]['value']}")

