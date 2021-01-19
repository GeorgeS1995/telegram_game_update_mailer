from peewee import Model, CharField
from core.db import db


class WarzoneGameNews(Model):
    warzone_news_url = CharField(max_length=2048)

    class Meta:
        database = db
