import telegram
import os
from dotenv import load_dotenv
import requests
from requests.exceptions import ReadTimeout, ConnectionError
import time


def main():
    load_dotenv()
    devman_token = os.environ['DEVMAN_API_TOKEN']
    tg_bot_token = os.environ['TELEGRAM_BOT_TOKEN']
    tg_chat_id = os.environ['TG_CHAT_ID']

    bot = telegram.Bot(token=tg_bot_token)

    url = "https://dvmn.org/api/long_polling/"
    headers = {
        'Authorization': devman_token
    }
    timestamp = None

    while True:
        try:
            params = {}
            if timestamp:
                params['timestamp'] = timestamp
                    
            response = requests.get(url, headers=headers, params=params)
            checked_lessons = response.json()
            
            if checked_lessons['status'] == 'timeout':
                timestamp = checked_lessons['timestamp_to_request']

            elif checked_lessons['status'] == 'found':
                lesson_title = checked_lessons['new_attempts'][0]['lesson_title']
                check_result = checked_lessons['new_attempts'][0]['is_negative']
                lesson_url = checked_lessons['new_attempts'][0]['lesson_url']

                if check_result:
                    check_result_text = 'К сожалению, в работе нашлись ошибки.'
                else:
                    check_result_text = 'Преподавателю все понравилось, можно приступать к следующему уроку!'

                lesson_link = f'<a href="{lesson_url}">{lesson_title}</a>'
                text = f'У вас проверили работу "{lesson_link}"\n\n{check_result_text}'

                bot.send_message(chat_id=tg_chat_id, text=text, parse_mode='HTML')
                timestamp = checked_lessons['last_attempt_timestamp']

        except ReadTimeout:
            continue

        except ConnectionError:
            time.sleep(600)
            continue


if __name__ == '__main__':
    main()