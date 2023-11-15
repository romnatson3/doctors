import requests
import logging
from django.conf import settings
from bot.exception import ResponseException, TelegramException
from math import ceil


class Empty():
    def __bool__(self):
        return False

    def __getattr__(self, name):
        return Empty()

    def __repr__(self):
        return 'False'


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
        return Empty()


def batched(lst, num):
    i = 0
    batch = []
    for _ in range(ceil(len(lst) / num)):
        batch.append(lst[i:i + num])
        i += num
    return batch


def send_message(method, **data):
    url = f'https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/{method}'
    if 'photo' in data:
        file = data.pop('photo')
        with open(file, 'rb') as f:
            response = requests.post(url, data=data, files={'photo': f})
    else:
        response = requests.post(url, data=data)
    if response.status_code == 200:
        response_data = DotAccessibleDict(response.json())
        if response_data.ok:
            return response_data.result
        else:
            logging.error(f'user_id={data.get("chat_id")} {response_data}')
            raise TelegramException(f'user_id={data.get("chat_id")} {response_data}')
    else:
        logging.error(f'user_id={data.get("chat_id")} status={response.status_code} {response.text}')
        raise ResponseException(f'user_id={data.get("chat_id")} status={response.status_code} {response.text}')
