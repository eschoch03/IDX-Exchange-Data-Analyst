# -*- coding: utf-8 -*-
"""
IDX Exchange Internship - Weeks 2-3: Mortgage Rate Enrichment
Datasets: Sold and listings (January 2024 - September 2026)

@author: Emma

Fetches the 30-year fixed mortgage rate (MORTGAGE30US) from FRED, resamples
it from weekly to monthly averages, and merges it onto both validated
datasets using a year_month key. Saves both enriched datasets as new CSVs.

The script is organized in cells that follow the handbook steps.
Run the cells in order.
"""

# %% Cell 1: Fetch the mortgage rate data from FRED

import pandas as pd

folder = r"C:\Users\Emma\MY_IDX_FILES\csv"

url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
mortgage = pd.read_csv(url, parse_dates=['observation_date'])
mortgage.columns = ['date', 'rate_30yr_fixed']

print("Weekly rates loaded:", len(mortgage))
print(mortgage.tail())

# %% Cell 2: Resample weekly rates to monthly averages

mortgage['year_month'] = mortgage['date'].dt.to_period('M')
mortgage_monthly = (
    mortgage.groupby('year_month')['rate_30yr_fixed']
    .mean()
    .reset_index())

# monthly averages for the months covered by the MLS data
in_range = mortgage_monthly[mortgage_monthly['year_month'] >= '2024-01']
print(in_range.to_string(index=False))

# %% Cell 3: Load the validated datasets and create the year_month key

sold = pd.read_csv(folder + r"\sold_residential_validated.csv", low_memory=False)
listings = pd.read_csv(folder + r"\listings_residential_validated.csv", low_memory=False)
print("Sold rows:", len(sold))
print("Listings rows:", len(listings))

# sold dataset keyed off CloseDate
sold['year_month'] = pd.to_datetime(sold['CloseDate']).dt.to_period('M')

# listings dataset keyed off ListingContractDate
listings['year_month'] = pd.to_datetime(
    listings['ListingContractDate']
).dt.to_period('M')

# %% Cell 4: Merge the monthly rates onto both datasets

sold_with_rates = sold.merge(mortgage_monthly, on='year_month', how='left')
listings_with_rates = listings.merge(mortgage_monthly, on='year_month', how='left')

# a left merge should keep every row, so counts should match the originals
print("Sold rows after merge:", len(sold_with_rates))
print("Listings rows after merge:", len(listings_with_rates))

# %% Cell 5: Validate the merge

# unmatched rows (rate should not be null)
print("Sold rows missing a rate:", sold_with_rates['rate_30yr_fixed'].isnull().sum())
print("Listings rows missing a rate:", listings_with_rates['rate_30yr_fixed'].isnull().sum())

# preview
print(
    sold_with_rates[
        ['CloseDate', 'year_month', 'ClosePrice', 'rate_30yr_fixed']
    ].head())

# %% Cell 6: Save both enriched datasets

sold_with_rates.to_csv(folder + r"\sold_with_rates.csv", index=False)
print("Saved sold_with_rates.csv")

listings_with_rates.to_csv(folder + r"\listings_with_rates.csv", index=False)
print("Saved listings_with_rates.csv")
