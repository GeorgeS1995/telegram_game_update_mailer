import os

BOT_API_TOKEN = os.getenv('BOT_API_TOKEN')
UPDATE_FREQUENCY = int(os.getenv('UPDATE_FREQUENCY'))
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
NEWS_TEMPLATE = "Игра: {game}\n" \
                "Новость: {title}\n" \
                "Ссылка: {url}\n" \
                "Время публикации: {date}\n" \
                "Краткое описание: {contents}\n"
