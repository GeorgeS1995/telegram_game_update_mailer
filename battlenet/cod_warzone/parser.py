import asyncio
from datetime import datetime
import requests
from bs4 import BeautifulSoup, Tag
from battlenet.cod_warzone.models import WarzoneGameNews
from core.logger import logger
from core.mailer_core import Mailer
from core.setting import NEWS_TEMPLATE


class WarzoneNewsParser:
    NEWS_URL = "https://www.callofduty.com/ru/blog"
    GAME = "COD WARZONE"

    def _get_html(self):
        try:
            r = requests.get(self.NEWS_URL)
            return r.content
        except requests.exceptions.RequestException as err:
            logger.error(f"Can't get callofduty.com DOM: {err}")
            return

    def _is_new_news(self, news: Tag) -> bool:
        if isinstance(news, Tag) and news.get('data-game') and news['data-game'] == 'warzone':
            url = news.select_one('a')['href']
            _, created = WarzoneGameNews.get_or_create(warzone_news_url=url)
            return created

    def _get_news_date(self, input_date_str: str) -> str:
        date = datetime.strptime(input_date_str, '%B %d, %Y')
        return datetime.strftime(date, '%Y-%m-%d')

    def _parse_warzone_news(self, news: Tag, parsed_news: list):
        title = news.select_one('a > div.post-right > div.post-header > h3').text
        url = self.NEWS_URL + news.select_one('a')['href']
        date = self._get_news_date(news.select_one('a > div.post-right > div.post-header > h4').text)
        contents = news.select_one('a > div.post-right > div.post-content > p').text
        parsed_news.append(NEWS_TEMPLATE.format(game=self.GAME, title=title, url=url, contents=contents, date=date))

    def parse_warzone_news(self) -> list:
        html = self._get_html()
        if not html:
            return []
        soup = BeautifulSoup(html, 'html.parser')

        news_list = soup.select_one('body > div.root.responsivegrid > div > '
                                    'div.blog-aggregator.aem-GridColumn.aem-GridColumn--default--12 > div > '
                                    'div.blog-content-container > div.blog-content > div.blog-entries').children
        parsed_news = []
        for n in news_list:
            if isinstance(n, Tag) and n.get('data-game') and n['data-game'] == 'warzone':
                url = n.select_one('a')['href']
                _, created = WarzoneGameNews.get_or_create(warzone_news_url=url)
                if created:
                    self._parse_warzone_news(n, parsed_news)
                    continue
                break
        parsed_news.reverse()
        return parsed_news

    def news_sender(self):
        @Mailer.add_news_source()
        async def _news_sender() -> list:
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, self.parse_warzone_news)


warzone_news = WarzoneNewsParser()
warzone_news.news_sender()
