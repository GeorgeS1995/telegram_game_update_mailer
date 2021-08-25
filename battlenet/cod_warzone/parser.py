import asyncio
from datetime import datetime
import requests
from bs4 import BeautifulSoup, Tag
from battlenet.cod_warzone.models import WarzoneGameNews
from core.logger import logger
from core.mailer_core import Mailer
from core.setting import NEWS_TEMPLATE


class WarzoneNewsParser:
    NEWS_URL = "https://www.callofduty.com"
    GAME = "COD WARZONE"
    EMPTY_MSG_ATTR = "N/A"

    def _get_html(self, url=None):
        if not url:
            url = self.NEWS_URL + "/ru/blog"
        try:
            r = requests.get(url)
            return r.content
        except requests.exceptions.RequestException as err:
            logger.error(f"Can't get callofduty.com DOM: {err}")
            return

    def _get_news_date(self, soup: BeautifulSoup) -> str:
        input_date_str = soup.select_one('#main > div.inner-container > div.blog-header-container > div.text > div > '
                                         'div.mobile-layout > div.date-by-lines > p.dateline').text
        date = datetime.strptime(input_date_str, '%B %d, %Y')
        return datetime.strftime(date, '%Y-%m-%d')

    def _get_news_content(self, soup: BeautifulSoup) -> str:
        content = soup.select_one('#main > div.inner-container > div.blog-body-container > div.body-content > div'
                                  ' > div:nth-child(1) > div > div').text
        return content if len(content) < 300 else f"{content[:300]}..."

    def _parse_warzone_news(self, news: Tag, parsed_news: list):
        title = news.select_one('div > div.text > div.title > h2 > a').text.strip()
        url_news_str = news.select_one('a')['href']
        url = url_news_str if url_news_str.startswith("http") else self.NEWS_URL + url_news_str
        soup = BeautifulSoup(self._get_html(url=url), 'html.parser')
        try:
            date = self._get_news_date(soup)
            contents = self._get_news_content(soup)
        except AttributeError:
            logger.error(f"Can't parse news with url: {url}")
            parsed_news.append(NEWS_TEMPLATE.format(game=self.GAME, title=title, url=url,
                                                    contents=self.EMPTY_MSG_ATTR, date=self.EMPTY_MSG_ATTR))
            return
        parsed_news.append(NEWS_TEMPLATE.format(game=self.GAME, title=title, url=url, contents=contents, date=date))

    def _get_news_list(self, soup: BeautifulSoup):
        first_news_div = soup.select_one('body > div.root.responsivegrid > div > div:nth-child(2) > section > div > '
                                         'div > div > div > section > div.inner-container > div')
        yield first_news_div.select_one('div.col-lg-8.hero-left > div')
        eight_next_news = soup.select_one('div.col-lg-4.hero-right > ul')
        for li in eight_next_news.find_all("li"):
            yield li.div
        second_news_div = soup.select_one('body > div.root.responsivegrid > div > div:nth-child(3) > section > div > '
                                          'div > div > div > section > div')
        yield second_news_div.select_one('div.row.top-grid > div.col-lg-8.left > div')
        for n in second_news_div.select_one('div.row.top-grid > div.col-lg-4.right > div').\
                find_all("div", class_="col-md-6 col-lg-12"):
            yield n.div
        for n in second_news_div.select_one('div.row.row-cols-1.row-cols-md-2.row-cols-lg-3.bottom-grid').children:
            yield n

    def parse_warzone_news(self) -> list:
        html = self._get_html()
        if not html:
            return []
        soup = BeautifulSoup(html, 'html.parser')

        news_list = self._get_news_list(soup)
        parsed_news = []
        for n in news_list:
            if isinstance(n, Tag) and n.get('data-game') and 'warzone' in n['data-game']:
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
