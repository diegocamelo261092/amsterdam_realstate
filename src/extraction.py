import pickle
import scraper
import sqlalchemy
import config
import pandas
from pararius_parameters import pararius_dict

# Import Dictionary
pararius_dictionary = pararius_dict()

# Extract Scrapped Data
results = scraper.RealEstateScrapingHandler(pararius_dictionary).handle_extraction()

# Database Connection
db_name = config.mysql_db_name
db_host_name = config.mysql_db_host_name
db_user_name = config.mysql_user
db_password = config.mysql_password

database_connection = sqlalchemy.create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'
            .format(db_user_name, db_password, db_host_name, db_name)).connect()

# Write to DB
results.to_sql(con=database_connection, name='test_table', if_exists='append', index=False)
