import sys
sys.path.append('/Users/daniel/github_uf829d/amsterdam_realstate/daniel')
import aiohttp
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time as tm
import math
import pickle as p
import File_manager as fm
import os
import bs4 as bs4


def pickle_store(item):
    p.dump(item, open("temp.p", "wb"))


def pickle_load():
    data = p.load(open("temp.p", "rb"))
    return data

class AsyncWebScraper(object):
    # headless webscraper class
    def __init__(self):
        self.urls = []
        self.fetch_results = []

    async def fetch(self, session, url):
        async with session.get(url) as response:
            html_text = await response.text()
            return url, html_text

    async def main(self):
        tasks = []
        headers = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.1 Safari/537.13"}
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False), headers=headers) as session:
            for url in self.urls:
                tasks.append(self.fetch(session, url))

            self.fetch_results = await asyncio.gather(*tasks)

    def get_html(self, urls):
        self.urls = urls
        asyncio.run(self.main())
        return self.fetch_results

class SeleniumWebScraper(object):

    def __init__(self, headless=True, eager_load=False):
        self.driver_path = '/Users/daniel/PycharmProjects/Funda/chromedriver'
        self.cookie_path = '/Users/daniel/PycharmProjects/Funda/cookie.p'
        self.options = Options()
        self.options.headless = headless
        self.options.add_argument("user-data-dir=selenium")
        if eager_load:
            self.options.page_load_strategy = 'eager'

        self.driver = webdriver.Chrome(options=self.options, executable_path=self.driver_path)

    def keep_running(self):
        while True:
            tm.sleep(5)

    def fetch_urls(self, urls):
        fetch_results = []
        for url in urls:
            self.driver.get(url)
            fetch_results.append(self.driver.page_source)

        self.close()
        return fetch_results

    def fast_loading(self):
        pass

    def close(self):
        self.driver.quit()

    def fetch_urls_multi_tab(self, urls_requested, max_tabs=5):
        fetch_results = []
        loop_number = int(math.ceil(len(urls_requested) / max_tabs))
        for loop in range(loop_number):
            loop_urls = urls_requested[loop * max_tabs:(loop * max_tabs) + max_tabs]
            for x in range(len(loop_urls)):
                if x <= (len(self.driver.window_handles)-1):
                    self.driver.switch_to.window(self.driver.window_handles[x])
                    self.driver.get(loop_urls[x])
                else:
                    self.driver.execute_script('''window.open("{}","_blank");'''.format(loop_urls[x]))
                fetch_results.append(self.driver.page_source)
        self.close()
        return fetch_results

class Pararius(object):

    def __init__(self):
        self.base_url = 'https://www.pararius.nl/koopwoningen/amsterdam'
        self.loop_url = 'https://www.pararius.com/apartments/amsterdam/apartment/page-'
        self.urls = []
        self.pages = []
        self.output_paths = []
        self.fm = fm.FileManager("Pararios_files")
        self.fm.folder_handler_multiple(['output'], ['output'])
        self.scraper = AsyncWebScraper()

    def get_html(self, urls):
        return self.scraper.get_html(urls)

    def get_base_html(self):
        return self.get_html([self.base_url])

    def store_output(self, data, file_name):
        location = os.path.join(self.fm.get_folder(['output']), file_name)
        with open(location, 'w') as f:
            f.write(data)

    def get_base_pages(self):
        html = str(self.get_base_html())
        soup = bs4.BeautifulSoup(html)
        pages = soup.find_all(attrs={'class': 'pagination__item'})
        pass

    def url_to_html_pickle(self, url):
        pickle_store(self.get_html([url])[0][1])
        pass

class Funda(object):

    def __init__(self):
        self.fm = fm.FileManager("Pararius_files")
        self.fm.folder_handler_multiple(['output'], ['output'])
        self.base_url = 'https://www.funda.nl/koop/amsterdam/'
        self.page_base_url = 'https://www.funda.nl/koop/amsterdam/p'
        self.urls = []
        self.pages = []
        # self.scraper = SeleniumWebScraper(headless=False, eager_load=False)

    def get_base_html(self):
        # data = self.scraper.fetch_urls([self.base_url])
        # pickle_store(data)
        # return data
        return pickle_load()[0]

    def get_base_pages(self):
        html = self.get_base_html()
        soup = bs4.BeautifulSoup(html, features="html.parser")
        pages = soup.findall("div", {"class": "pagination__item"})
        for page in pages:
            print(page.txt)


    def create_loop_urls(self):
        for x in range(self.max_pages):
            self.urls.append(self.page_base_url+x)

    def loop_through_urls(self):
        self.scraper.fetch_urls_multi_tab(self.urls)


if __name__ == '__main__':
    data = Funda()
    data.get_base_pages()

