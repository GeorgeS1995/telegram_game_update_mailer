import pytest
from core.mailer_core import Mailer


@pytest.fixture()
def tg_bot():
    Mailer.GAME_NEWS_SOURCE = []
    bot = Mailer(token="1:t", validate_token=False, without_db=True)
    bot.ACTIVE_CHATS = {1}
    yield bot
