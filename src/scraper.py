# ---------- PACKAGES IMPORT -------------

# Packages
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import datetime as dt
import math
import bs4 as bs4
import urllib
import os
import pandas as pd

# -------- FUNCTIONS DEFINITION -----------

def soup_list(list):
    """
    This function is used to apply beautiful soup over a list of html text unparsed and returns the list of text parsed
    :param:
    - list, this is a list of unformated html text which requires formatting through beautifulsoup
    """
    return [bs4.BeautifulSoup(not_soup, features="html.parser") for not_soup in list]


def multi_function_applier(data, functions):
    """
    This function allows the application of multiple functions past in as a list over the same data set
    :param:
    - data, is the data over which the function should be applied
    - functions, is a list of variable functions which should be applied over the earlier mentioned data
    """
    if isinstance(functions, list):
        for f in functions:
            data = f(data)
            pass
    else:
        data = functions(data)
    return data

# ---------- CLASS WEB SCRAPER  -----------------

class SeleniumWebScraper(object):

    """
    This class is used to handle multiple url requests and returns their respective html text.
    Furthermore, the url requests can either be handled by the single tab requester function: fetch_urls
    or instead through the more efficient multi tab requester, which allows the requesting of multiple urls over
    several pages.

    Attributes
    ----------
    driver_path : str
        description of the attribute

    Methods
    -------
    fetch_urls(urls)
        Description of the method
    """

    def __init__(self, headless=True, full_loading=False, aws_options=False):
        """
        Parameters
        ----------
        headless: bool

        """

        self.driver_path = os.getcwd() + '/chromedriver'
        self.options = Options()
        if aws_options:
            self.chrome_driver_web_optiosn()

        self.options.headless = headless
        self.options.add_argument("user-data-dir=selenium")
        if not full_loading:
            self.options.page_load_strategy = 'none'
        self.driver = object

    def chrome_driver_web_options(self):
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--window-size=1280x1696')
        self.options.add_argument('--user-data-dir=/tmp/user-data')
        self.options.add_argument('--hide-scrollbars')
        self.options.add_argument('--enable-logging')
        self.options.add_argument('--log-level=0')
        self.options.add_argument('--v=99')
        self.options.add_argument('--single-process')
        self.options.add_argument('--data-path=/tmp/data-path')
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--homedir=/tmp')
        self.options.add_argument('--disk-cache-dir=/tmp/cache-dir')
        self.options.add_argument(
            'user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')
        self.options.binary_location = os.getcwd() + "/bin/headless-chromium"

    def fetch_urls(self, urls):
        """

        :param urls:
        :return:
        """
        self.driver = webdriver.Chrome(options=self.options, executable_path=self.driver_path)
        fetch_results = []
        for url in urls:
            self.driver.get(url)
            fetch_results.append(self.driver.page_source)

        self.close()
        return fetch_results

    def close(self): # Was a method really needed for this?
        """

        :return:
        """
        self.driver.quit()

    def fetch_urls_multi_tab(self, urls_requested, max_tabs=5):
        """

        :param urls_requested:
        :param max_tabs:
        :return:
        """
        self.driver = webdriver.Chrome(options=self.options, executable_path=self.driver_path)
        fetch_results = []
        loop_number = int(math.ceil(len(urls_requested) / max_tabs))

        for x in range(max_tabs - 1):
            self.driver.execute_script('''window.open("{}","_blank");'''.format(x))

        for loop in range(loop_number):
            loop_urls = urls_requested[loop * max_tabs:(loop * max_tabs) + max_tabs]
            for x in range(len(loop_urls)):
                self.driver.switch_to.window(self.driver.window_handles[x])
                self.driver.get(loop_urls[x])

            for x in range(len(loop_urls)):
                self.driver.switch_to.window(self.driver.window_handles[x])
                fetch_results.append(self.driver.page_source)
            pass
        self.close()
        return fetch_results


class RealEstateScraper(SeleniumWebScraper):

    def __init__(self, search_dict):
        self.search_dict = search_dict

        self.output_name = 'listings_' + dt.datetime.today().strftime('%Y_%m_%d_%H%M')

        self.start_url = self.search_dict['base_page']

        self.base_url = urllib.parse.urlparse(self.start_url)[0] + "://" + urllib.parse.urlparse(self.start_url)[1]

        self.page_base_url = self.search_dict['page_base_url']

        self.indexes_urls = []
        self.max_page = 0

        super().__init__(headless=False, full_loading=True)

    def index_max_pages(self, soup):
        variables = self.search_dict['max_page_find']
        page = soup.find_all(variables[0], {variables[1]: variables[2]})
        page_index = [x.getText() for x in page]
        if len(variables) > 2:
            page_index = multi_function_applier(page_index, variables[3])
        self.max_page = int(max(page_index))
        self.max_page = 2

    def indexes_attributes(self):
        not_soup = self.fetch_urls([self.start_url])[0]
        self.index_max_pages(bs4.BeautifulSoup(not_soup, features="html.parser"))

        for x in range(1, self.max_page):
            self.indexes_urls.append(self.page_base_url + str(x))

        not_soup = []
        not_soup.extend(self.fetch_urls_multi_tab(self.indexes_urls))
        soup = soup_list(not_soup)

        indexes_column_names = [column[0] for column in self.search_dict['index_page_attributes']]
        indexes_attributes = []
        for s in soup:
            indexes_attributes.extend(self.attributes_from_page(s, self.search_dict['index_page_attributes'],
                                                                self.search_dict['index_page_blocks']))
        return indexes_column_names, indexes_attributes

    def listing_attributes(self, urls):
        not_soup = []
        not_soup.extend(self.fetch_urls_multi_tab(urls))
        soup = soup_list(not_soup)

        pages_column_names = ['link'] + [column[0] for column in self.search_dict['listings_page_attributes']]
        pages_attributes = []

        for s in soup:
            pages_attributes.extend(self.attributes_from_page(s, self.search_dict['listings_page_attributes']))

        for i in range(len(urls)):
            pages_attributes[i].insert(0, urls[i])

        return pages_column_names, pages_attributes

    def attributes_from_page(self, soup, find_variables, block_variables=None):
        attributes = []

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


class RealEstateScrapingHandler(RealEstateScraper):

    def __init__(self, variable_dict):
        self.search_dict = variable_dict
        self.current_date = dt.datetime.today().strftime('%Y_%m_%d')

        # self.historic_extraction_pandas = object

        # self.extraction_path = ""
        self.extraction_listing_pandas = ""
        # self.extraction_pages_pandas = ""

        super().__init__(variable_dict)

    def handle_extraction(self, batch_size=20, diego=True):
        indexes_column_names, indexes_attributes = self.indexes_attributes()
        self.extraction_listing_pandas = pd.DataFrame(indexes_attributes)
        self.extraction_listing_pandas.columns = indexes_column_names

        if not diego:

            listing_page_urls = self.extraction_listing_pandas['link'].tolist()

            pages_attributes_list = []
            pd_merged = object

            for i in range(0, len(listing_page_urls), batch_size):
                print('Finalized processing of listing page urls {} of {}'.format(i, len(listing_page_urls)))
                batch = listing_page_urls[i:i + batch_size]
                page_column_names, page_attributes = self.listing_attributes(batch)
                pages_attributes_list.extend(page_attributes)

                pd_pages = pd.DataFrame(pages_attributes_list)
                pd_pages.columns = page_column_names

                pd_merged = pd.merge(self.extraction_listing_pandas, pd_pages, how='left', left_on=['link'],
                                     right_on=['link'])
            return pd_merged
        else:
            return self.extraction_listing_pandas
