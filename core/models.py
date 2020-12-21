from peewee import Model, BigIntegerField
from core.db import db


class Chats(Model):
    """ Store a subscriber chat id list if bot was reloaded """
    recipient = BigIntegerField()

    class Meta:
        database = db
