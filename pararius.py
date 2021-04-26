# Created by: Diego Camelo
# This code aims to scrape data from Funda.nl, a Dutch real state marketplace
# Data is stored into a database and then insights are delivered to my personal email

# ---------- Packages -----------
# ===============================

from selenium import webdriver
import pandas as pd
import time

# ------- Web Scrapping ---------
# ===============================

# Navigation Settings

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument('--start-maximized')
options.add_argument('--disable-extensions')

PATH = "/Users/Diego/opt/chromedriver"
driver = webdriver.Chrome(PATH, options=options)

# For Loop to iterate over multiple pages
pages = 5

# Empty List of Elements
addresses_list = []
zipcodes_list = []
prices_list = []
details_list = []

for page in range(1, pages, 1):

    # Webpage: Funda, a Dutch real state marketplace
    url = 'https://www.pararius.nl/koopwoningen/amsterdam/page-' + str(page)
    driver.get(url)
    time.sleep(1)

    # Try to click on cookie only on the first page
    if page == 1:
        cookie = driver.find_element_by_xpath('// *[ @ id = "onetrust-accept-btn-handler"]')
        cookie.click()
    else:
        pass

    # Get lists of all relevant elements
    addresses = driver.find_elements_by_xpath(
        '//*[contains(@class, "listing-search-item__link listing-search-item__link--title")]')
    zipcodes = driver.find_elements_by_xpath('//*[contains(@class, "listing-search-item__location")]')
    prices = driver.find_elements_by_xpath('//*[contains(@class, "listing-search-item__price")]')
    details = driver.find_elements_by_xpath('//*[contains(@class, "illustrated-features__content")]')

    # Create text lists for all elements

    for i in range(len(addresses)):
        addresses_list.append(addresses[i].text)

    for i in range(len(zipcodes)):
        zipcodes_list.append(zipcodes[i].text)

    for i in range(len(prices)):
        prices_list.append(prices[i].text)

    for i in range(len(details)):
        details_list.append(details[i].text)

    # Cleaning of scrapped lists

    # Details contain multiple elements
    relevant_fields = ['woonopp', 'kamers', 'bouwjaar']
    matches = filter(lambda item: any(word in item for word in relevant_fields), details_list)
    filtered_details_list = list(matches)

    # Extract key elements from list every third position
    areas_list = []
    rooms_list = []
    years_list = []

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

    prices_list_corrected = []
    n = 0
    while n < len(prices_list):
        prices_list_corrected.append(prices_list[n])
        n += 2

driver.quit()

# Check that all lists have the same length
lengths = [len(addresses_list), len(zipcodes_list), len(prices_list_corrected),
           len(areas_list), len(rooms_list), len(years_list)]

while True:
    try:
        all(length == 10 for length in lengths)
        print("Yay! The lengths of the lists of attributes are equal!\n")
        break
    except ValueError:
        print("Oops! The lengths of the lists of attributes are not equal.\n")

# Create Initial Data Frame
col_names = ['Address', 'Zipcodes', 'Price (EUR)', 'Area (m2)', '# Rooms', 'Year Built']
page_data = pd.DataFrame(list(zip(addresses_list, zipcodes_list, prices_list_corrected,
                                  areas_list, rooms_list, years_list)))
page_data.columns = col_names

print(page_data.head())

# ------- Data Cleaning ---------
# ===============================