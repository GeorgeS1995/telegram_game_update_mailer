import asyncio
import datetime
from typing import Union
from core.logger import logger
from core.mailer_core import Mailer
import aiohttp
from steam.models import SteamGame, SteamGameNews


class SteamApiHandler:
    NEWS_URL = "https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/"
    UPDATE_FEED = "steam_community_announcements"
    CONTENT_LENGTH = 350
    NEWS_TEMPLATE = "Игра: {game}\n" \
                    "Новость: {title}\n" \
                    "Ссылка: {url}\n" \
                    "Время публикации: {date}\n" \
                    "Краткое описание: {contents}\n"
    TIME_FORMAT = "%Y-%m-%d, %H:%M:%S"

    def _parse_news(self, game: SteamGame, new: dict, news: list) -> None:
        SteamGameNews.insert(game=game, steam_news_id=new['gid'], steam_date=new['date']).execute()
        date_time = datetime.datetime.fromtimestamp(new['date'])
        news.append(self.NEWS_TEMPLATE.format(game=game.label, title=new['title'], url=new['url'],
                                              contents=new['contents'], date=date_time.strftime(self.TIME_FORMAT)))

    def _get_bunch_from_db(self, ids: set):
        return SteamGameNews.select().where(SteamGameNews.steam_news_id.in_(ids))

    def _compare_with_db(self, news_bunch) -> list:
        news_bunch_ids = {int(n['gid']) for n in news_bunch}
        db_news = self._get_bunch_from_db(news_bunch_ids)
        db_news = {n.steam_news_id for n in db_news}
        fresh_news_id = news_bunch_ids - db_news
        return [n for n in news_bunch if int(n['gid']) in fresh_news_id]

    async def _request_news_bunch(self, session: aiohttp.ClientSession, params: dict) -> Union[list, None]:
        async with session.get(self.NEWS_URL, params=params) as resp:
            if not resp.ok:
                text = await resp.text()
                logger.error(f"Can't get news for steam. code: {resp.status}, text: {text}")
                return
            response = await resp.json()
            return response['appnews']['newsitems']

    async def _get_new_news(self, game: SteamGame) -> list:
        news = []
        async with aiohttp.ClientSession() as session:
            params = {"appid": game.steam_app_id, "feeds": self.UPDATE_FEED, "maxlength": self.CONTENT_LENGTH}
            while True:
                news_bunch = await self._request_news_bunch(session, params)
                new_news_in_bunch = self._compare_with_db(news_bunch)
                if not news_bunch or not new_news_in_bunch:
                    break
                [self._parse_news(game, new, news) for new in new_news_in_bunch]
                params['enddate'] = news_bunch[-1]['date'] - 1
        news.reverse()
        return news

    def news_sender(self):
        @Mailer.add_news_source()
        async def _news_sender() -> list:
            result = []
            games = SteamGame.select()
            [result.extend(n) for n in await asyncio.gather(*[self._get_new_news(game) for game in games])]
            return result


steam = SteamApiHandler()
steam.news_sender()
