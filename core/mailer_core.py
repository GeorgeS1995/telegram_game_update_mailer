import asyncio
from typing import Callable
from aiogram import Bot, types
from aiogram.utils import exceptions
from core.logger import logger
from core.models import Chats


class Mailer(Bot):
    """ Telegram bot api handler, all methods starts with cmd_ will register as bot command
    and must able to recive msg as parameter"""
    BOT_COMMANDS = []
    GAME_NEWS_SOURCE = []

    def __init__(self, *args, update_frequency=10, without_db=False, **kwargs):
        super(Mailer, self).__init__(*args, **kwargs)
        self.update_frequency = update_frequency
        Bot.set_current(self)
        if without_db:
            return
        self.ACTIVE_CHATS = {chat.recipient for chat in Chats.select()}

    def _delete_from_chats(self, chat_id):
        self.ACTIVE_CHATS.remove(chat_id)
        Chats.delete().where(Chats.recipient == chat_id).execute()

    async def send_safe_message(self, chat_id: int, text: str, disable_notification: bool = False) -> bool:
        """
        Safe messages sender

        :param chat_id:
        :param text:
        :param disable_notification:
        :return:
        """
        try:
            await super(Mailer, self).send_message(chat_id, text, disable_notification=disable_notification)
        except exceptions.BotBlocked:
            logger.error(f"Target [ID:{chat_id}]: blocked by user")
            self._delete_from_chats(chat_id)
        except exceptions.ChatNotFound:
            logger.error(f"Target [ID:{chat_id}]: invalid user/chat ID")
            self._delete_from_chats(chat_id)
        except exceptions.RetryAfter as e:
            logger.error(f"Target [ID:{chat_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds.")
            await asyncio.sleep(e.timeout)
            return await self.send_safe_message(chat_id, text)
        except exceptions.UserDeactivated:
            logger.error(f"Target [ID:{chat_id}]: user/chat is deactivated")
            self._delete_from_chats(chat_id)
        except exceptions.TelegramAPIError:
            logger.exception(f"Target [ID:{chat_id}]: failed")
        else:
            logger.debug(f"Target [ID:{chat_id}]: success")
            return True
        return False

    @classmethod
    def add_news_source(cls) -> Callable:
        def decorator(informer):
            cls.GAME_NEWS_SOURCE.append(informer)
        return decorator

    async def broadcaster(self) -> None:
        while True:
            logger.debug(f"Start mailer for chats: {self.ACTIVE_CHATS}")
            if not self.GAME_NEWS_SOURCE:
                logger.warning("Empty game sources, setup a game sources by adding @Mailer.add_news_source() decorator")
            informers = [informer() for informer in self.GAME_NEWS_SOURCE]
            for sheduled_informer in asyncio.as_completed(informers):
                updates = await sheduled_informer
                for update in updates:
                    senders = [self.send_safe_message(chat, update) for chat in self.ACTIVE_CHATS]
                    await asyncio.gather(*senders)
            logger.debug(f"Mailer successfully ended for chats: {self.ACTIVE_CHATS}")
            await asyncio.sleep(self.update_frequency)

    async def command_runner(self):
        offset = None
        while True:
            try:
                results = await self.get_updates(offset=offset, timeout=20)
            except asyncio.exceptions.TimeoutError:
                logger.error("Can't get updates, retrying via 1 min")
                await asyncio.sleep(60)
                continue
            if results:
                offset = max([r.update_id for r in results]) + 1
                cmd_handlers = [getattr(self, cmd.message.text.replace("/", "cmd_"))(cmd.message) for cmd in results]
                await asyncio.gather(*cmd_handlers)

    async def set_bot_commands(self):
        """ Register all func startswith cmd_ as user command """
        self.BOT_COMMANDS = [types.BotCommand(f.replace("cmd_", ""), str(getattr(self, f).__doc__)) for f in dir(self)
                             if f.startswith("cmd_")]
        r = await self.set_my_commands(self.BOT_COMMANDS)
        if not r:
            logger.error("Can't set command's list for bot")

    async def cmd_start(self, message: types.Message) -> None:
        """ Повторить приветсвенное сообщение """
        self.ACTIVE_CHATS.add(message.chat.id)
        if not Chats.get_or_none(Chats.recipient == message.chat.id):
            Chats.insert(recipient=message.chat.id).execute()
        await self._welcome_msg(message)

    async def cmd_help(self, message: types.Message) -> None:
        """ О боте """
        await self._welcome_msg(message)

    async def _welcome_msg(self, message: types.Message):
        msg = "Я бот рассыльный информации о обновлениях для игр, пожалуйста не игнорируйте мои сообщения " \
              "и своевременно обновляйте игры"
        logger.debug(f"New subsciber, chat id {message.chat.id}")
        await message.reply(msg)
