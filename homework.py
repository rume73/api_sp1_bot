import os
import time
import json

import logging
import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')


URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}


logging.basicConfig(
    level=logging.DEBUG,
    filename='bot.log',
    filemode='w',
    datefmt='%Y-%m-%d,%H:%M:%S',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    status = homework.get('status')
    if status == 'reviewing':
        verdict = 'Работа взята в ревью'
        return f'"{homework_name}"!\n\n{verdict}'
    elif status == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    elif status == 'approved':
        verdict = ('Ревьюеру всё понравилось, можно приступать '
                   'к следующему уроку.')
    else:
        verdict = 'Что-то пошло не так'
        logging.error('Не удалось получить данные из homework')
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    homework_statuses = requests.get(URL, headers=headers,
                                     params={'from_date': current_timestamp})
    try:
        return homework_statuses.json()
    except requests.RequestException as e:
        logging.error(f'Ошибка у бота {e}')
    try:
        return homework_statuses.json()
    except json.JSONDecodeError as e:
        logging.error(f'Ошибка распаковки json() {e}')


def send_message(message, bot_client):
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(new_homework.get(
                                                   'homeworks')[0]), bot)
            current_timestamp = new_homework.get('current_date',
                                                 current_timestamp)
            time.sleep(300)

        except Exception as e:
            print(f'Бот столкнулся с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
