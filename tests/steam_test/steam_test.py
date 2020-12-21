from typing import NamedTuple
import aiohttp
import pytest
from steam.steam import SteamApiHandler


class FakeClientResponse:
    def __init__(self, status=None, text=None):
        self.ok = False
        self.status = status
        self._text = text

    async def text(self):
        return self._text

    def release(self):
        pass


class DBTuple(NamedTuple):
    steam_news_id: int


@pytest.mark.asyncio
class TestSteamApiHndler:
    @pytest.mark.parametrize("data", [{"status": 400, "text": "error"}, {"status": 500, "text": "error"}])
    async def test_steam_not_ok_response(self, monkeypatch, data):
        async def mocked_request(self, m, s, *args, **kwargs):
            return FakeClientResponse(**data)
        steam = SteamApiHandler()
        monkeypatch.setattr(aiohttp.ClientSession, "_request", mocked_request)
        async with aiohttp.ClientSession() as session:
            resp = await steam._request_news_bunch(session, {})
        assert not resp

    @pytest.mark.parametrize("data", [{"steam": [{'gid': 1}, {'gid': 2}], "db": [1], "new_news": [{'gid': 2}]}])
    def test_compare_with_db(self, monkeypatch, data):
        def mocked_db_data(self, id):
            return [DBTuple(id) for id in data['db']]
        monkeypatch.setattr(SteamApiHandler, "_get_bunch_from_db", mocked_db_data)
        steam = SteamApiHandler()
        new_steam_news = steam._compare_with_db(data['steam'])
        assert new_steam_news == data['new_news']
