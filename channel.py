import schedule
from time import sleep

from bot import send_to_channel
from data import find_books, update_is_sent
import config


def send_to_channel_job():
    for book in find_books(config.db_name, is_sent_to_channel='0'):
        sent_message = f'<b>{book["title"]}</b>\n{book["author"]}\n<i>{book["pub_name"]}</i>'

        send_to_channel(text=sent_message, photo_url=book['image_path'], message_type='photo', url=book['url'],
                        chat_id=config.tech_chat_id, keyboard=True)

        update_is_sent(config.db_name, book['url'])

        sleep(4)


schedule.every().day.at("12:00").do(send_to_channel_job)

while True:
    schedule.run_pending()
    sleep(1)
