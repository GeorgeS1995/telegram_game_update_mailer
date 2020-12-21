from peewee import PostgresqlDatabase
from core.setting import POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

db = PostgresqlDatabase(POSTGRES_DB, user=POSTGRES_USER, password=POSTGRES_PASSWORD, host="db", port=5432)
