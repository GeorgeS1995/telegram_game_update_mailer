import asyncio
from asyncio.exceptions import CancelledError
import pytest
from core.mailer_core import Mailer


@pytest.mark.asyncio
class TestBotCore:
    async def test_add_news_source_decorator(self, tg_bot, monkeypatch):
        test_msg = "test msg"

        async def mocked_send_safe_message(self, c, u):
            assert u == test_msg
            fut.set_result("done")

        monkeypatch.setattr(Mailer, "send_safe_message", mocked_send_safe_message)

        @Mailer.add_news_source()
        async def informer():
            return [test_msg]

        async def stopper():
            await fut
            task.cancel()

        loop = asyncio.get_running_loop()
        fut = loop.create_future()

        task = asyncio.create_task(tg_bot.broadcaster())
        try:
            await asyncio.gather(task, stopper())
        except CancelledError:
            pass

    async def test_set_command_test(self, tg_bot, monkeypatch):
        async def mocked_set_my_command(self, commands: list):
            assert "test_route" in [c._values['command'] for c in commands]
            return True

        monkeypatch.setattr(Mailer, "set_my_commands", mocked_set_my_command)

        tg_bot.cmd_test_route = lambda: None

        await tg_bot.set_bot_commands()
