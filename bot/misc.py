import requests
from django.conf import settings


class DotAccessibleDict(dict):
    def __init__(self, dictionary):
        for key, value in dictionary.items():
            if key == 'from':
                key = 'from_user'
            if isinstance(value, dict):
                self.__dict__[key] = DotAccessibleDict(value)
            else:
                self.__dict__[key] = value
            self[key] = value

    def __getattr__(self, name):
        self.__dict__.get(name)


class ResponseException(Exception):
    pass


def send_messages(method, **data):
    url = f'https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/{method}'
    response = requests.post(url, data=data)
    if response.status_code == 200:
        response_data = DotAccessibleDict(response.json())
        if response_data.ok:
            return response_data.result
        else:
            raise ResponseException(response_data.description)
    else:
        raise ResponseException(response.status_code)
