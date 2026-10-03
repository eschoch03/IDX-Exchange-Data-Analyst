# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 17:44:54 2026

@author: Emma

IDX Exchange Internship - Week 1: Monthly Dataset Aggregation
(Combines the monthly Sold and Listing CSVs, keeps only Residential,
and saves two new CSVs.)
"""
import glob
import pandas as pd

folder = r"C:\Users\Emma\MY_IDX_FILES\csv"

# ----------------------------------------------------------------------
# SOLD
# ----------------------------------------------------------------------

# find every file in the folder that starts with CRMLSSold
sold_files = sorted(glob.glob(folder + r"\CRMLSSold*.csv"))
print("Sold files found:", len(sold_files))

# read each file and add it to a list
sold_list = []
sold_total = 0   # running total of rows across the monthly files
for file in sold_files:
    df = pd.read_csv(file, low_memory=False)
    print(file, len(df))
    sold_list.append(df)
    sold_total = sold_total + len(df)

print("Sold rows before concat (sum of monthly files):", sold_total)

# stack all the monthly files into one dataset
sold = pd.concat(sold_list)
print("Sold rows after concat:", len(sold))

# keep only residential
sold_res = sold[sold["PropertyType"] == "Residential"]
print("Sold rows after Residential filter:", len(sold_res))

# save
sold_res.to_csv(folder + r"\sold_combined_residential.csv", index=False)

# ----------------------------------------------------------------------
# LISTINGS
# ----------------------------------------------------------------------

listing_files = sorted(glob.glob(folder + r"\CRMLSListing*.csv"))
print("Listing files found:", len(listing_files))

listing_list = []
listing_total = 0
for file in listing_files:
    df = pd.read_csv(file, low_memory=False)
    print(file, len(df))
    listing_list.append(df)
    listing_total = listing_total + len(df)

print("Listing rows before concat (sum of monthly files):", listing_total)

listings = pd.concat(listing_list)
print("Listing rows after concat:", len(listings))

listings_res = listings[listings["PropertyType"] == "Residential"]
print("Listing rows after Residential filter:", len(listings_res))

listings_res.to_csv(folder + r"\listings_combined_residential.csv", index=False)

# ----------------------------------------------------------------------
# ROW COUNTS (run on 10/3/2026, January 2024 through September 2026)
# ----------------------------------------------------------------------
# SOLD (33 monthly files)
#   Before concat (sum of monthly files):        736,333
#   After concat / before Residential filter:    736,333
#   After Residential filter:                    495,195
#
# LISTINGS (33 monthly files)
#   Before concat (sum of monthly files):        1,046,356
#   After concat / before Residential filter:    1,046,356
#   After Residential filter:                    665,393
#
# notes:
#   - Concatenation did not add or drop any rows in either dataset.
#   - Months 202605-202609 (sold and listings) and listings 202601 were
#     pulled with the extraction scripts and all other months came from FTP.
