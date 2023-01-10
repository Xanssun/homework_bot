import logging
import os
import sys
import time
import requests
import telegram

from dotenv import load_dotenv
from http import HTTPStatus

from exceptions import (SendmessageError, PracticumAPIError)

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


def check_tokens():
    """Проверка на наличие переменных."""
    if all([TELEGRAM_TOKEN, PRACTICUM_TOKEN,
            TELEGRAM_CHAT_ID]) is False:
        logging.critical('Отсутсвуют переменные')
        raise sys.exit('Программа принудительно останавливается '
                        'так как нет переменных')
    return True


def send_message(bot, message):
    """Отправка сообщения ботом."""
    text = message
    try:
        bot.send_message(TELEGRAM_CHAT_ID, text)
        logging.debug(f'Отправил сообщения {text}')
    except telegram.error.TelegramError as error:
        logging.error(f'Сбой в работе программы: {error}')
        raise SendmessageError(f'Ошибка отправки сообщения{error}')


def get_api_answer(timestamp):
    """Делает запрос."""
    payload = {'from_date': timestamp}
    try:
        homework_statuses = requests.get(
            ENDPOINT, headers=HEADERS, params=payload)
    except requests.RequestException as error:
        raise PracticumAPIError(f'Ошибка запроса {error}')
    if homework_statuses.status_code != HTTPStatus.OK:
        logging.error('сбои при запросе к эндпоинту ',
                      f'{homework_statuses.status_code}')
        raise PracticumAPIError('Yandex лежит')
    return homework_statuses.json()


def check_response(response):
    """Проверка ответа Json."""
    if not isinstance(response, dict):
        raise TypeError('Не словарь')
    if not response.get('homeworks'):
        raise KeyError('Нет ключа в словаре')
    value = response['homeworks']
    if not isinstance(value, list):
        raise TypeError('Не список')
    if value:
        return response['homeworks'][0]
    else:
        raise IndexError('Пустой список')


def parse_status(homework):
    """Проверка статуса домашней работы."""
    homework_status = homework.get('status')
    homework_name = homework.get('homework_name')
    if 'homework_name' not in homework:
        raise Exception('Ошибка названия домашки')
    if homework_status not in HOMEWORK_VERDICTS:
        logging.error('Неверный статус домашки')
        raise NameError('Недокументированный статус домашней работы')
    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    answer = ''
    check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(timestamp)
            homework = check_response(response)
            message = parse_status(homework)
            if answer != message:
                send_message(bot, message)
            timestamp = response.get('timestamp')
        except IndexError:
            message = 'Статус работ не изменился'
            if answer != message:
                send_message(bot, message)
            logging.debug('В ответе нет новых статусов')
        except Exception as error:
            logging.error(f'Сбой в работе программы: {error}')
            send_message(bot, message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
