# -*- coding: utf-8 -*-
"""
IDX Exchange Internship - Weeks 2-3: Dataset Structuring and Validation
Dataset: Listings (January 2024 - September 2026)

@author: Emma

Inspects the combined listings dataset, documents property types, filters to
Residential, reports missing values, and summarizes key numeric fields.
Saves the filtered dataset as a new CSV.

The script is organized in cells that follow the handbook sections.
Run the cells in order.
"""

# %% Cell 1: Load the combined listings dataset

import glob
import pandas as pd

folder = r"C:\Users\Emma\MY_IDX_FILES\csv"

# The Week 1 output is already filtered to Residential. To document all
# property types, combined dataset is rebuilt here from the monthly files.
listing_files = sorted(glob.glob(folder + r"\CRMLSListing*.csv"))
print("Listing files found:", len(listing_files))

listing_list = []
for file in listing_files:
    df = pd.read_csv(file, low_memory=False)
    listing_list.append(df)

listings = pd.concat(listing_list, ignore_index=True)
print("Combined listings dataset loaded.")

# %% Cell 2: Inspect structure

print(listings.columns.tolist())
print(listings.head())

# number of rows and columns
print("Rows and columns:", listings.shape)

# column data types
print(listings.dtypes.to_string())

# note to self: remove duplicate columns with ".1" in later weeks

# %% Cell 3: Property types and residential filter

# unique property types
print("Unique property types:", listings["PropertyType"].unique())

# count and percentage share of each property type
print(listings["PropertyType"].value_counts(dropna=False))
type_share = listings["PropertyType"].value_counts(normalize=True, dropna=False) * 100
print(type_share.round(2))

# filter to Residential only since (other types are priced on a different basis and would distort price metrics)
rows_before = len(listings)
listings = listings[listings.PropertyType == 'Residential']
rows_after = len(listings)

print("Rows before Residential filter:", rows_before)
print("Rows after Residential filter: ", rows_after)
print("Rows removed:                  ", rows_before - rows_after)

# %% Cell 4: Missing value analysis

# missing count and percentage per column
missing_count = listings.isnull().sum()
missing_pct = (missing_count / len(listings) * 100).round(2)

# null-count summary table, sorted from most to least missing
missing_report = pd.DataFrame({
    "missing_count": missing_count,
    "missing_pct": missing_pct,})

missing_report["over_90_pct"] = missing_report["missing_pct"] > 90
missing_report = missing_report.sort_values("missing_pct", ascending=False)
print(missing_report.to_string())

# columns flagged as more than 90% missing
high_missing = missing_report[missing_report["over_90_pct"]]
print("Columns above 90% missing:", len(high_missing))
print(high_missing.index.tolist())

# %% Cell 5: Numeric distribution review (percentile summaries)

# three fields required by deliverable
deliverable_fields = ["ClosePrice", "LivingArea", "DaysOnMarket"]

# the other six key numeric fields
other_fields = [
    "ListPrice", "OriginalListPrice", "LotSizeAcres",
    "BedroomsTotal", "BathroomsTotalInteger", "YearBuilt",]

# all nine key numeric fields
numeric_fields = deliverable_fields + other_fields

# display settings so wide tables print in full with readable numbers
pd.set_option("display.float_format", "{:,.2f}".format)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

percentiles = [0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99]

# min, max, mean, median and percentiles for ClosePrice, LivingArea, DaysOnMarket
numeric_summary = listings[deliverable_fields].describe(percentiles=percentiles)
print(numeric_summary)

# same summary but for all nine key numeric fields
print(listings[numeric_fields].describe(percentiles=percentiles))

# %% Cell 6: Drop high-missing columns and save

# core fields are retained even if mostly missing (same core fields as the sold script so both validated datasets handled consistently)
core_fields = numeric_fields + [
    "PropertyType", "CloseDate", "ListingContractDate", "CountyOrParish"]

# drop columns above 90% missing and not core fields
cols_to_drop = []
for col in high_missing.index:
    if col not in core_fields:
        cols_to_drop.append(col)

print("Columns dropped:", cols_to_drop)
print("Shape before dropping columns:", listings.shape)
listings = listings.drop(columns=cols_to_drop)
print("Shape after dropping columns: ", listings.shape)

listings.to_csv(folder + r"\listings_residential_validated.csv", index=False)
print("Saved listings_residential_validated.csv")
