# -*- coding: utf-8 -*-
"""
IDX Exchange Internship - Weeks 2-3: Dataset Structuring and Validation
Dataset: Sold transactions (January 2024 - September 2026)

@author: Emma

Inspects the combined sold dataset, documents property types, filters to
Residential, reports missing values, and summarizes key numeric fields.
Saves the filtered dataset as a new CSV.

The script is organized in cells that follow the handbook sections.
Run the cells in order.
"""

# %% Cell 1: Load the combined sold dataset

import glob
import pandas as pd
import matplotlib.pyplot as plt

folder = r"C:\Users\Emma\MY_IDX_FILES\csv"

# The Week 1 output is already filtered to Residential. To document all
# property types, the combined dataset is rebuilt here from the monthly files.
sold_files = sorted(glob.glob(folder + r"\CRMLSSold*.csv"))
print("Sold files found:", len(sold_files))

sold_list = []
for file in sold_files:
    df = pd.read_csv(file, low_memory=False)
    sold_list.append(df)

sold = pd.concat(sold_list, ignore_index=True)
print("Combined sold dataset loaded.")

# %% Cell 2: Inspect structure

print(sold.columns.tolist())
print(sold.head())

# number of rows and columns
print("Rows and columns:", sold.shape)

# column data types
print(sold.dtypes.to_string())

# %% Cell 3: Property types and residential filter

# unique property types
print("Unique property types:", sold["PropertyType"].unique())

# count and percentage share of each property type
print(sold["PropertyType"].value_counts(dropna=False))
type_share = sold["PropertyType"].value_counts(normalize=True, dropna=False) * 100
print(type_share.round(2))

# filter to Residential only since (other types are priced on a different basis and would distort sale price metrics)
rows_before = len(sold)
sold = sold[sold.PropertyType == 'Residential']
rows_after = len(sold)

print("Rows before Residential filter:", rows_before)
print("Rows after Residential filter: ", rows_after)
print("Rows removed:                  ", rows_before - rows_after)

# %% Cell 4: Missing value analysis

# missing count and percentage per column
missing_count = sold.isnull().sum()
missing_pct = (missing_count / len(sold) * 100).round(2)

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

# three fields required by the handbook deliverable
deliverable_fields = ["ClosePrice", "LivingArea", "DaysOnMarket"]

# the other six key numeric fields named in the handbook
other_fields = [
    "ListPrice", "OriginalListPrice", "LotSizeAcres",
    "BedroomsTotal", "BathroomsTotalInteger", "YearBuilt",]

# all nine key numeric fields (the deliverable fields first)
numeric_fields = deliverable_fields + other_fields

# display settings so wide tables print in full with readable numbers
pd.set_option("display.float_format", "{:,.2f}".format)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

percentiles = [0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99]

# min, max, mean, median and percentiles for ClosePrice, LivingArea, DaysOnMarket
numeric_summary = sold[deliverable_fields].describe(percentiles=percentiles)
print(numeric_summary)

# the same summary but for all nine key numeric fields
print(sold[numeric_fields].describe(percentiles=percentiles))

# %% Cell 6: Numeric distribution review (histograms and boxplots)

for field in numeric_fields:
    values = sold[field].dropna()

    # histograms limited to the 1st-99th percentile so extreme values do not 
    # compress them to a single bar, but boxplots show all values so outliers
    # remain visible there.
    low = values.quantile(0.01)
    high = values.quantile(0.99)
    middle = values[(values >= low) & (values <= high)]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 3.5))

    ax1.hist(middle, bins=50)
    ax1.set_title(field + " - histogram (1st to 99th percentile)")
    ax1.set_xlabel(field)
    ax1.set_ylabel("Number of homes")

    ax2.boxplot(values, vert=False)
    ax2.set_title(field + " - boxplot (all values)")
    ax2.set_xlabel(field)
    ax2.set_yticks([])

    plt.tight_layout()
    plt.show()

# %% Cell 7: Other misc intern question responses:

# percentage of homes sold above vs. below list price (rows missing either price excluded)
priced = sold.dropna(subset=["ClosePrice", "ListPrice"])
above = (priced["ClosePrice"] > priced["ListPrice"]).mean() * 100
below = (priced["ClosePrice"] < priced["ListPrice"]).mean() * 100
at_list = (priced["ClosePrice"] == priced["ListPrice"]).mean() * 100
print("Sold above list price (%):", round(above, 2))
print("Sold below list price (%):", round(below, 2))
print("Sold at list price (%):   ", round(at_list, 2))

# date consistency: close date before listing date (invalid dates converted to blanks rather than raising an error)
close_date = pd.to_datetime(sold["CloseDate"], errors="coerce")
listing_date = pd.to_datetime(sold["ListingContractDate"], errors="coerce")
print("Rows where close date is before listing date:",
      (close_date < listing_date).sum())

# counties with highest median close price
county_stats = sold.groupby("CountyOrParish")["ClosePrice"].agg(["median", "count"])
print(county_stats.sort_values("median", ascending=False).head(10))

# %% Cell 8: Drop high-missing columns and save

# core fields are retained even if mostly missing (the nine key numeric
# fields plus the fields used for filtering and the suggested questions)
core_fields = numeric_fields + [
    "PropertyType", "CloseDate", "ListingContractDate", "CountyOrParish"]

# drop columns that are above 90% missing and not core fields
cols_to_drop = []
for col in high_missing.index:
    if col not in core_fields:
        cols_to_drop.append(col)

print("Columns dropped:", cols_to_drop)
print("Shape before dropping columns:", sold.shape)
sold = sold.drop(columns=cols_to_drop)
print("Shape after dropping columns: ", sold.shape)

sold.to_csv(folder + r"\sold_residential_validated.csv", index=False)
print("Saved sold_residential_validated.csv")
