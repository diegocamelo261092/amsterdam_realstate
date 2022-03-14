from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import uuid
import bs4
import os
from parameters import pararius_dict


def to_list(string_or_list):
    if not isinstance(string_or_list, (list, tuple)):
        string_or_list = [string_or_list]
    return string_or_list

def soup_list(not_soups):
    """
    This function is used to apply beautiful soup over a list of html text unparsed and returns the list of text parsed
    :param:
    - list, this is a list of unformated html text which requires formatting through beautifulsoup
    """
    not_soups = to_list(not_soups)
    return [bs4.BeautifulSoup(not_soup, features="html.parser") for not_soup in not_soups]


class SeleniumWebScraper(object):
    # class was created with as intention to reuse the code for the scraper for funda
    # separate class ensures that the SeleniumWebScraper can be optimized without having to change codes in either
    # RealEstateScraper (pararius) and future funda scraper

    def __init__(self, docker_run=True):
        self._tmp_folder = '/tmp/{}'.format(uuid.uuid4())

        if not os.path.exists(self._tmp_folder):
            os.makedirs(self._tmp_folder)

        if not os.path.exists(self._tmp_folder + '/user-data'):
            os.makedirs(self._tmp_folder + '/user-data')

        if not os.path.exists(self._tmp_folder + '/data-path'):
            os.makedirs(self._tmp_folder + '/data-path')

        if not os.path.exists(self._tmp_folder + '/cache-dir'):
            os.makedirs(self._tmp_folder + '/cache-dir')

        chrome_options = webdriver.ChromeOptions()
        if docker_run:
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1280x1696')
            chrome_options.add_argument('--user-data-dir={}'.format(self._tmp_folder + '/user-data'))
            chrome_options.add_argument('--hide-scrollbars')
            chrome_options.add_argument('--enable-logging')
            chrome_options.add_argument('--log-level=0')
            chrome_options.add_argument('--v=99')
            chrome_options.add_argument('--single-process')
            chrome_options.add_argument('--data-path={}'.format(self._tmp_folder + '/data-path'))
            chrome_options.add_argument('--ignore-certificate-errors')
            chrome_options.add_argument('--homedir={}'.format(self._tmp_folder))
            chrome_options.add_argument('--disk-cache-dir={}'.format(self._tmp_folder + '/cache-dir'))
            chrome_options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                        'Chrome/61.0.3163.100 Safari/537.36')
            chrome_options.binary_location = os.getcwd() + "/bin/headless-chromium"
            self.driver = webdriver.Chrome(chrome_options=chrome_options)

        else:
            chrome_options.page_load_strategy = 'normal'
            self.driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)

    def fetch_urls(self, urls):
        fetch_results = []
        urls = to_list(urls)

        for url in urls:
            self.driver.get(url)
            fetch_results.append(bs4.BeautifulSoup(self.driver.page_source, features="html.parser"))
        self.close()
        return fetch_results

    def close(self):
        self.driver.quit()


class RealEstateScraper(SeleniumWebScraper):

    def __init__(self, search_dict, docker_run=True):
        super().__init__(docker_run)
        self.real_estate_dict = search_dict

    def read_base_page(self):
        return self.fetch_urls(self.real_estate_dict['base_page'])[0].getText()

    def attributes_from_page(self, urls, find_variables, block_variables=None):

        urls = to_list(urls)
        soups = self.fetch_urls(urls)

        attributes = []

        for soup in soups:

            # Note to self:
            # In selenium wrapper:
            #   Created init function wrapper for selenium
            #   Created test function to run wrapper and child classes without binary and chromeless options
            #   To do store cookie data to prevent are you a robot authentication

            # in RealEstateScraper:
            #   Created base page code
            #   To do recreate function to recognize and get html blocks (1 block =  1 listing on listing page)
            #   To do recreate reading the attributes from html blocks
            #   To do create function for time out/robot auth question


            if block_variables is not None:
                soup = soup.find_all(block_variables[0], {block_variables[1]: block_variables[2]})
            else:
                soup = [soup]

            for s in soup:
                attribute_block = []
                for a in find_variables:
                    try:
                        if a[4]:
                            raw = s.find(a[1], {a[2]: a[3]})['href']
                            if self.base_url not in raw:
                                raw = self.base_url + raw
                        else:
                            raw = s.find(a[1], {a[2]: a[3]}).getText()
                        if len(a) > 5:
                            raw = a[5](raw)
                    except:
                        raw = None
                    attribute_block.append(raw)
                attributes.append(attribute_block)
            return attributes


if __name__ == "__main__":
    test_run = RealEstateScraper(pararius_dict(), docker_run=False)
    print(test_run.read_base_page())