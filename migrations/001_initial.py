"""Peewee migrations -- 001_initial.py.

Some examples (model - class or model name)::

    > Model = migrator.orm['model_name']            # Return model in current state by name

    > migrator.sql(sql)                             # Run custom SQL
    > migrator.python(func, *args, **kwargs)        # Run python code
    > migrator.create_model(Model)                  # Create a model (could be used as decorator)
    > migrator.remove_model(model, cascade=True)    # Remove a model
    > migrator.add_fields(model, **fields)          # Add fields to a model
    > migrator.change_fields(model, **fields)       # Change fields
    > migrator.remove_fields(model, *field_names, cascade=True)
    > migrator.rename_field(model, old_field_name, new_field_name)
    > migrator.rename_table(model, new_table_name)
    > migrator.add_index(model, *col_names, unique=False)
    > migrator.drop_index(model, *col_names)
    > migrator.add_not_null(model, *field_names)
    > migrator.drop_not_null(model, *field_names)
    > migrator.add_default(model, field_name, default)

"""

import peewee as pw

try:
    import playhouse.postgres_ext as pw_pext
except ImportError:
    pass

SQL = pw.SQL

GAME = {
    "steam": [
        {"label": "Counter-Strike: Global Offensive", "steam_app_id": 730},
        {"label": "Dota 2", "steam_app_id": 570},
        {"label": "PLAYERUNKNOWN'S BATTLEGROUNDS", "steam_app_id": 578080},
        {"label": "Apex Legends", "steam_app_id": 1172470},
        {"label": "Counter-Strike", "steam_app_id": 10},
    ]
}


def migrate(migrator, database, fake=False, **kwargs):
    """Write your migrations here."""

    @migrator.create_model
    class Chats(pw.Model):
        id = pw.AutoField()
        recipient = pw.BigIntegerField()

        class Meta:
            table_name = "chats"

    @migrator.create_model
    class SteamGame(pw.Model):
        id = pw.AutoField()
        label = pw.CharField(max_length=250)
        steam_app_id = pw.IntegerField()

        class Meta:
            table_name = "steamgame"

    @migrator.create_model
    class SteamGameNews(pw.Model):
        id = pw.AutoField()
        game = pw.ForeignKeyField(backref='steamgamenews_set', column_name='game_id', field='id',
                                  model=migrator.orm['steamgame'])
        steam_news_id = pw.BigIntegerField()
        steam_date = pw.TimestampField()

        class Meta:
            table_name = "steamgamenews"

    @migrator.python
    def add_steam_games():
        with migrator.database.atomic():
            for game in GAME['steam']:
                SteamGame.create(**game)


def rollback(migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""

    migrator.remove_model('steamgamenews')

    migrator.remove_model('steamgame')

    migrator.remove_model('chats')
