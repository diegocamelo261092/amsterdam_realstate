# Created by: Diego Camelo

# This code analysis data scraped from Pararius.nl, a Dutch real state marketplace
# It provides basic summary statistics and plots and delivers them to the email.

# ------ TO DO's ---------------
# ===============================

# todo: results unique per week (Done)
# todo: plotting, don't repeat myself, create function (Progress)
# todo: create subset formed by last 4 weeks
# todo: enhance location data (Progress)
# todo: upload code into GitHub
# todo: weekly comparison fields (e.g apartment dropped)
# todo: explore price per m2 vs price


# ---------- Packages -----------
# ===============================

from sqlalchemy import create_engine
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as md
from matplotlib.ticker import StrMethodFormatter, MultipleLocator
import seaborn as sns
import time

# ------- Configuration ---------
# ===============================

pd.set_option('display.max_columns', None)
pd.options.display.width = 100


# ------- Functions -------------
# ===============================

def plot_func(plot, title, x, y, type):
    """

    :param plot: Seaborn type AxesSubplot to be configured
    :param title: Title of the plot
    :param x: Label of the x axis
    :param y: Label of the y axis
    :param type: Type of plots or x axis, relational or categorical
    :return: Nothing, set parameters of plot.

    """

    # Title and Labels
    plot.fig.suptitle(title)
    plot.set(xlabel=x, ylabel=y)

    # x-axis settings

    if type == "rel":
        plot.ax.xaxis.set_major_locator(md.WeekdayLocator(byweekday=0))
        plot.ax.xaxis.set_major_formatter(md.DateFormatter('%Y-%m-%d'))
        plot.ax.xaxis.set_minor_locator(md.DayLocator(interval=1))
        plot.set_xticklabels(rotation=90)
    elif type == "cat":
        pass
    else:
        pass

    # y-axis settings (Thousands
    plot.ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
    plot.ax.yaxis.set_major_locator(MultipleLocator(500))
    # plot.ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
    plot.set_xticklabels(rotation=90)

    # Tight Layout
    plt.tight_layout()


# ------- Data Import -----------
# ===============================

print('Initializing Connection to DB\n')
time.sleep(2)
engine = create_engine("mysql+pymysql://root:261092Dmc!@localhost:3306/realstatedb")
con = engine.connect()
rs = con.execute("select * from realstatedb.pararius")
apartments = pd.DataFrame(rs.fetchall())
apartments.columns = rs.keys()
print('Successfully Connected to DB\n')

time.sleep(3)

del (con, rs)

# -- Initial Data Transformation --
# =================================

# Add price per square meter
apartments['price_per_m2'] = apartments['price_eur'] / apartments['area_m2']

# -- Initial Data Cleaning --------
# =================================

print("Original Table has " + str(len(apartments)) + " apartments\n")

print("Cleaning table...\n")
time.sleep(3)

# 1. Drop Rows with NAs
apartments = apartments.dropna()

# 2. Keep Only Invalid Pages
apartments = apartments[apartments['validity'] == 1]
apartments = apartments.drop(columns='validity')

# 3. Remove Projects
apartments = apartments[~apartments['address'].str.contains("Project")]

# 4.  Data Type Transformation

apartments['price_eur'] = apartments['price_eur'].astype(int)
apartments['area_m2'] = apartments['area_m2'].astype(int)
apartments['results'] = apartments['results'].astype(int)
apartments['zipcode'] = apartments['zipcode'].str.replace(r'[^\d]', '', regex=True).astype('int')

apartments['snapshot_date'] = pd.to_datetime(apartments['snapshot_date'])  # Object to datetime
apartments['snapshot_date'] = apartments['snapshot_date'].dt.floor('d')  # Truncate to date

apartments['snapshot_week'] = apartments['snapshot_date'] - pd.to_timedelta(
    apartments['snapshot_date'].dt.dayofweek, unit='d')  # Truncate to week

apartments['snapshot_week_str'] = apartments['snapshot_week'].dt.date

# 5. Drop Duplicates
apartments = apartments.drop_duplicates()
apartments = apartments.drop_duplicates(subset=['snapshot_week', 'address'])

# 6. Remove Outliers
apartments = apartments[apartments['year_built'] > 1300]
apartments = apartments[apartments['zipcode'] >= 1000]

# 7. Reset Index
apartments.reset_index(drop=True, inplace=True)

print("Cleaning finished!\n")
time.sleep(1)
print("Clean table has " + str(len(apartments)) + " apartments\n")

# ---- Popular Zipcodes -----------
# =================================

# Step required to extract districts

zipcodes = apartments['zipcode']
unique_zipcodes = zipcodes.drop_duplicates()

unique_zipcodes.to_sql('unique_zipcodes', engine, if_exists='replace', index=False)

del zipcodes

# --- Basic Data Description ----
# ===============================

print("DATA FRAME INFORMATION:\n")
apartments.info()  # To check data types
print("\n")
time.sleep(3)

print("DATA FRAME SHAPE:\n")
print(apartments.shape)  # To check number of rows and columns
print("\n")
time.sleep(3)

print("SUMMARY STATISTICS:\n")
print(apartments.describe().apply(lambda s: s.apply('{0:.5f}'.format)))  # Basic summary statistics
print("\n")
time.sleep(3)

print("HISTORY OF RUNS:\n")
print(apartments['snapshot_week'].value_counts().sort_index())  # Display history of runs and results
print("\n")
time.sleep(3)

# ------- DATA EXPLORATION ------
# ===============================

# ---- Price per m2 over time -----------
# ----------------------------------------

# Table with aggregates
trend = apartments.groupby('snapshot_week'). \
    agg(number_of_aparments=('address', 'count'),
        results=('results', 'max'),
        avg_price_per_m2=('price_per_m2', 'mean'),
        median_price_per_m2=('price_per_m2', 'median'))

# Median Plot
g = sns.relplot(x='snapshot_week', y='median_price_per_m2', data=trend, kind='line', aspect=1.5)
plot_func(g, "Historical Median Price per m2", "Snapshot Week", "Pricer per m2 (EUR)", "rel")

# Average Plot + 95% CI
g = sns.relplot(x='snapshot_week', y='price_per_m2', data=apartments, kind='line')
plot_func(g, "Historical Average Price per m2", "Snapshot Week", "Pricer per m2 (EUR)", "rel")

# Box Plot over Time
g = sns.catplot(x='snapshot_week_str', y='price_per_m2', data=apartments, kind="box", sym='')
plot_func(g, "Boxplot: Average Price per m2", "Snapshot Week", "Pricer per m2 (EUR)", "cat")

# --- Price per m2 per Neighbourhood -----
# ----------------------------------------

neighbourhoods = apartments.groupby('neighbourhood'). \
    agg(number_of_apartments=('address', 'count'),
        avg_price_per_m2=('price_per_m2', 'mean'),
        median_price_per_m2=('price_per_m2', 'median')
        ).sort_values(by='number_of_apartments', ascending=False).reset_index()

# Box Plot for Popular Neighbourhoods

popular = neighbourhoods.nlargest(25, "number_of_apartments")['neighbourhood'].unique().tolist()

popular_apartments = apartments[apartments['neighbourhood'].isin(popular)]

# Box Plot: price per m2 per neighbourhood

plt.figure(figsize=(22, 10))
g = sns.catplot(x='neighbourhood', y='price_per_m2', data=popular_apartments, kind="box", sym='')
plot_func(g, "Price per m2 (EUR) distribution for top 25 neighbourhoods by # of apartments",
          "Neighbourhood", "Boxplot: Average Price per M2", "cat")

# ------ Price per m2 vs Price  ----------
# ----------------------------------------

# ------ Price per m2 vs Price  ----------
# ----------------------------------------

# ----------- Price vs Area  -------------
# ----------------------------------------


# ------- CLOSE CONNECTION ------
# ===============================

con.close()
