import asyncio
import importlib
import os
from aiogram.utils.exceptions import NetworkError
from peewee_migrate import Router
from core.logger import logger
from core.db import db
from core.mailer_core import Mailer
from core.setting import BOT_API_TOKEN, UPDATE_FREQUENCY


def load_modules():
    project_files = os.listdir(os.getcwd())
    for f in project_files:
        if os.path.isdir(f) and "__init__.py" in os.listdir(os.path.join(os.getcwd(), f)) and f != "core":
            [importlib.import_module(f"{f}.{m.replace('.py', '')}") for m in os.listdir(f) if m != "__init__.py"]


async def start_bot_jobs(bot: Mailer):
    tasks = [asyncio.create_task(getattr(bot, f)()) for f in ["set_bot_commands", "command_runner", "broadcaster"]]
    try:
        await asyncio.gather(*tasks)
    except NetworkError as err:
        logger.error(f"Network error, rerun main jobs via 1 min:{err}")
        await asyncio.sleep(60)
        [t.cancel() for t in tasks]
        await start_bot_jobs(bot)


async def main():
    load_modules()
    db.connect()
    router = Router(db)
    router.run()
    mailer = Mailer(token=BOT_API_TOKEN, update_frequency=UPDATE_FREQUENCY)
    await start_bot_jobs(mailer)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as err:
        logger.critical(f"Unhandled error: {err}")
        exit(1)
