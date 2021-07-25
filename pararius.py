# Created by: Diego Camelo
# This code aims to scrape data from Pararius.nl, a Dutch real state marketplace
# Data is stored into a database and then insights are delivered to my personal email

# ---------- Packages -----------
# ===============================

import time
import pandas as pd
from numpy import random
from datetime import date
from selenium import webdriver
from sqlalchemy import create_engine

# ---------- TO DO'S -----------
# ===============================

# todo: update github repository
# todo: Improve scrapping, avoid invalid pages.

# ===============================
# ------- Web Scrapping ---------
# ===============================

sleeping_time = random.choice([2, 3, 4, 5])

# Navigation Settings ------------
# --------------------------------

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument('--start-maximized')
options.add_argument('--disable-extensions')

PATH = "/Users/Diego/opt/chromedriver"
driver = webdriver.Chrome(PATH, options=options)

# Initial Page Actions -----------
# --------------------------------

print("Accessing First Page\n")

# Webpage: Pararius, a Dutch real state marketplace.
url = 'https://www.pararius.nl/koopwoningen/amsterdam/page-1'
driver.get(url)
time.sleep(sleeping_time)

# Click on Cookie
cookie = driver.find_element_by_xpath('// *[ @ id = "onetrust-accept-btn-handler"]')
cookie.click()
print("Cookie Clicked\n")
time.sleep(sleeping_time)

# Get Number of Pages
pages = driver.find_element_by_xpath('//*[contains(@class, "pagination__item")]/following-sibling::li[6]')
pages = int(pages.text)

# Get total results (a.k.a apartments listed)
results = driver.find_element_by_xpath('//*[contains(@class, "search-list-header__count")]').text

print("Number of Pages to Scrape: " + str(pages)+'\n')
time.sleep(sleeping_time)

# Variables Initialization -------
# --------------------------------

# Main Data Frame: Apartments
apartments = pd.DataFrame()

# Scrape All Pages ---------------
# --------------------------------

print("Web Scrapping Started")

for page in range(1, pages + 1, 1):

    # Variables Initialization

    apartments_local = pd.DataFrame()

    prices_large = []
    details_large = []

    addresses_list = []
    zipcodes_list = []
    prices_list = []
    areas_list = []
    rooms_list = []
    years_list = []
    page_list = []
    validity = []

    # Webpage: Funda, a Dutch real state marketplace
    url = 'https://www.pararius.nl/koopwoningen/amsterdam/page-' + str(page)
    print("Scrapping Page {0}".format(page))
    driver.get(url)
    time.sleep(sleeping_time)

    # Get lists of all relevant elements
    addresses = driver.find_elements_by_xpath(
        '//*[contains(@class, "listing-search-item__link listing-search-item__link--title")]')
    zipcodes = driver.find_elements_by_xpath('//*[contains(@class, "listing-search-item__location")]')
    prices = driver.find_elements_by_xpath('//*[contains(@class, "listing-search-item__price")]')
    details = driver.find_elements_by_xpath('//*[contains(@class, "illustrated-features__content")]')

    # Create text lists for all elements
    for i in range(len(addresses)):
        addresses_list.append(addresses[i].text)
        page_list.append(page)

    for i in range(len(zipcodes)):
        zipcodes_list.append(zipcodes[i].text)

    for i in range(len(prices)):
        prices_large.append(prices[i].text)

    for i in range(len(details)):
        details_large.append(details[i].text)

    # Details contain multiple elements
    relevant_fields = ['woonopp', 'kamers', 'bouwjaar']
    matches = filter(lambda item: any(word in item for word in relevant_fields), details_large)
    filtered_details_list = list(matches)

    # Extract key elements from list every third position
    for p in [1, 2, 3]:
        n = 0
        if p == 1:
            while n < len(filtered_details_list):
                areas_list.append(filtered_details_list[n])
                n += 3
        elif p == 2:
            subset = filtered_details_list[1:]
            while n < len(subset):
                rooms_list.append(subset[n])
                n += 3
        elif p == 3:
            subset = filtered_details_list[2:]
            while n < len(subset):
                years_list.append(subset[n])
                n += 3

    # Prices are duplicated, two rows per listing
    n = 0
    while n < len(prices_large):
        prices_list.append(prices_large[n])
        n += 2

    # Lengths Verification
    lengths = [len(addresses_list), len(zipcodes_list), len(prices_list),
               len(areas_list), len(rooms_list), len(years_list), len(page_list)]

    if lengths.count(lengths[0]) == len(lengths):
        validity = [True] * lengths[0]
        print("Yay! This page is valid!\n")
    else:
        validity = [False] * lengths[0]
        print("Oops! This page is invalid.\n")

    # Apartments Data Frame
    apartments_local = pd.DataFrame(list(zip(addresses_list, zipcodes_list, prices_list,
                                             areas_list, rooms_list, years_list, page_list, validity)))

    apartments = apartments.append(apartments_local, ignore_index=True, sort=True)

driver.quit()

# Delete unnecessary variables
del (PATH, addresses, apartments_local, cookie, details,
     details_large, driver, filtered_details_list, i,
     matches, n, options, p, page, pages, prices, prices_large,
     relevant_fields, subset, url, zipcodes, addresses_list,
     areas_list, lengths, page_list, prices_list,
     rooms_list, years_list, validity, zipcodes_list)

print("Web Scrapping Finished")

# ===============================
# ------- Data Processing -------
# ===============================

# Apartments Column Names
col_names = ['address', 'zipcode', 'price_eur', 'area_m2', 'n_rooms', 'year_built', 'page', 'validity']
apartments.columns = col_names

# Add constants
apartments['snapshot_date'] = date.today()
apartments['results'] = results

# Variables Types
apartments['results'] = apartments['results'].str.replace(r'[^\d]', '', regex=True).astype('int')
apartments['neighbourhood'] = apartments['zipcode'].str.extract(r'\((.+)\)')
apartments['zipcode'] = apartments['zipcode'].str[:7]
apartments['price_eur'] = apartments['price_eur'].str.replace(r'[^\d]', '', regex=True). \
    replace('', pd.NA).fillna(0).astype(int).replace(0, pd.NA)
apartments['area_m2'] = apartments['area_m2'].str.replace(r'[^\d]', '', regex=True).astype('int')
apartments['n_rooms'] = apartments['n_rooms'].str.replace(r'[^\d]', '', regex=True).astype('int')
apartments['year_built'] = apartments['year_built'].str.replace(r'[^\d]', '', regex=True).str[:4].astype('int')

# Change Column Order
neighbourhood = apartments['neighbourhood']
apartments.drop(labels=['neighbourhood'], axis=1, inplace=True)
apartments.insert(2, 'neighbourhood', neighbourhood)

# Display Data
pd.set_option('display.max_columns', None)
print(apartments.head())

print("Data is clean and ready to export.\n")
time.sleep(sleeping_time)

# Remove Variables
del neighbourhood

# ------- Data Export -----------
# ===============================
print("Connecting and Writing to DB.\n")
engine = create_engine("mysql+pymysql://root:261092Dmc!@localhost:3306/realstatedb")
apartments.to_sql('pararius', engine, if_exists='append', index=False)
print("Successfully Exported to DB")

del (engine, sleeping_time)

# ------- Data Exploration -----------
# ====================================

# Checks data for a single apartments
# print(apartments[apartments['address'].str.contains("Doddendaal")])
