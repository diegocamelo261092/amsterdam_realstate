# Created by: Diego Camelo
# This code aims to scrape data from Funda.nl, a Dutch real state marketplace
# Data is stored into a database and then insights are delivered to my personal email

# Packages ----------------------
from selenium import webdriver
import pandas as pd
import time

# Navigation Settings -----------
# options = webdriver.ChromeOptions()
# options.add_argument('--start-maximized')
# options.add_argument('--disable-extensions')

PATH = "/Users/Diego/opt/chromedriver"
driver = webdriver.Chrome(PATH)

# For Loop to iterate over multiple pages
pages = 5

# Empty List of Elements
addresses_list = []
zipcodes_list = []

for page in range(1, pages, 1):

    # Webpage: Funda, a Dutch real state marketplace
    url = 'https://www.pararius.nl/koopwoningen/amsterdam/page-' + str(page)
    driver.get(url)
    time.sleep(3)

    # Try to click on cookie only on the first page
    if page == 1:
        cookie = driver.find_element_by_xpath('// *[ @ id = "onetrust-accept-btn-handler"]')
        cookie.click()
    else:
        pass

    # Get lists of all relevant elements
    addresses = driver.find_elements_by_xpath('//*[contains(@class, "listing-search-item__link listing-search-item__link--title")]')
    zipcodes = driver.find_elements_by_xpath('//*[contains(@class, "listing-search-item__location")]')

    # Create text lists for all elements
    for i in range(len(addresses)):
        addresses_list.append(addresses[i].text)

    for i in range(len(zipcodes)):
        zipcodes_list.append(zipcodes[i].text)

# Data Frame from Lists
page_data = pd.DataFrame(list(zip(addresses_list, zipcodes_list)))


driver.quit()
