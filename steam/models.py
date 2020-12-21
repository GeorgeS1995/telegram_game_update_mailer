from peewee import Model, CharField, IntegerField, ForeignKeyField, BigIntegerField, TimestampField
from core.db import db


class SteamGame(Model):
    label = CharField(max_length=250)
    steam_app_id = IntegerField()

    class Meta:
        database = db


class SteamGameNews(Model):
    game = ForeignKeyField(SteamGame)
    steam_news_id = BigIntegerField()
    steam_date = TimestampField()

    class Meta:
        database = db
