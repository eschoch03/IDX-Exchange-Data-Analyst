# -*- coding: utf-8 -*-
"""
IDX Exchange Internship - Weeks 4-5: Data Cleaning and Preparation
Dataset: Sold transactions (January 2024 - September 2026)

@author: Emma

Cleans the enriched sold dataset (converts date fields, removes redundant
columns, handles missing and invalid values, flags date and geographic
issues, and saves analysis-ready CSV).

Script is organized in cells that follow the handbook sections.
Run the cells in order.
"""

# %% Cell 1: Load the enriched sold dataset

import pandas as pd

folder = r"C:\Users\Emma\MY_IDX_FILES\csv"

sold = pd.read_csv(folder + r"\sold_with_rates.csv", low_memory=False)

rows_start = len(sold)
print("Rows and columns:", sold.shape)

# %% Cell 2: Convert date fields to datetime

date_fields = [
    "CloseDate", "PurchaseContractDate",
    "ListingContractDate", "ContractStatusChangeDate"]

# data types before conversion (stored as text)
print(sold[date_fields].dtypes)

# convert each field (values that cant be read as a date become missing)
for col in date_fields:
    filled_before = sold[col].notnull().sum()
    sold[col] = pd.to_datetime(sold[col], errors="coerce")
    filled_after = sold[col].notnull().sum()
    print(col, "- unreadable dates set to missing:", filled_before - filled_after)

# data types after conversion
print(sold[date_fields].dtypes)

# %% Cell 3: Remove redundant and unnecessary columns

# redundant (same info is in another column)
redundant_cols = [
    "ListingKeyNumeric",                        # exact copy of ListingKey
    "ListAgentFirstName", "ListAgentLastName",  # combined in ListAgentFullName
    "LotSizeSquareFeet",                        # same as LotSizeAcres
    "LotSizeArea"]                              # mixed units, not reliable

# unnecessary (metadata not used for analysis)
metadata_cols = [
    "ListAgentEmail", "BuyerAgentMlsId", "ListAgentAOR", "BuyerAgentAOR",
    "BuyerOfficeAOR", "OriginatingSystemName", "OriginatingSystemSubName"]

print("Shape before removing columns:", sold.shape)
sold = sold.drop(columns=redundant_cols + metadata_cols)
print("Shape after removing columns: ", sold.shape)

# %% Cell 4: Handle missing values

# rows without a close price cant be used in any sale price metric
rows_before = len(sold)
sold = sold.dropna(subset=["ClosePrice"])
print("Rows removed for missing ClosePrice:", rows_before - len(sold))

# other missing values are left blank (they mostly mean the field doesnt
# apply or wasnt provided, and filling them in would invent data)
print(sold.isnull().sum().sort_values(ascending=False).head(15))

# %% Cell 5: Confirm numeric field types

numeric_fields = [
    "ClosePrice", "ListPrice", "OriginalListPrice", "LivingArea",
    "LotSizeAcres", "BedroomsTotal", "BathroomsTotalInteger",
    "DaysOnMarket", "YearBuilt", "rate_30yr_fixed"]

print(sold[numeric_fields].dtypes)

# %% Cell 6: Invalid numeric values

# count records that break the handbook's validity rules
print("ClosePrice <= 0:", (sold["ClosePrice"] <= 0).sum())
print("LivingArea <= 0:", (sold["LivingArea"] <= 0).sum())
print("DaysOnMarket < 0:", (sold["DaysOnMarket"] < 0).sum())
print("BedroomsTotal < 0:", (sold["BedroomsTotal"] < 0).sum())
print("BathroomsTotalInteger < 0:", (sold["BathroomsTotalInteger"] < 0).sum())

# ClosePrice <= 0: the sale itself is unusable, so the row is removed
rows_before = len(sold)
sold = sold[sold["ClosePrice"] > 0]
print("Rows removed for ClosePrice <= 0:", rows_before - len(sold))

# LivingArea <= 0 and DaysOnMarket < 0: the sale is still valid, so only
# the invalid value is set to missing (same approach as Cell 4)
sold["LivingArea"] = sold["LivingArea"].where(sold["LivingArea"] > 0)
sold["DaysOnMarket"] = sold["DaysOnMarket"].where(sold["DaysOnMarket"] >= 0)

# %% Cell 7: Date consistency flags

# expected order: ListingContractDate, PurchaseContractDate, then CloseDate
sold["listing_after_close_flag"] = sold["ListingContractDate"] > sold["CloseDate"]
sold["purchase_after_close_flag"] = sold["PurchaseContractDate"] > sold["CloseDate"]
sold["negative_timeline_flag"] = sold["PurchaseContractDate"] < sold["ListingContractDate"]

# number of records flagged by each check
flag_cols = [
    "listing_after_close_flag", "purchase_after_close_flag",
    "negative_timeline_flag"]
print(sold[flag_cols].sum())

# %% Cell 8: Geographic data checks

# missing coordinates
sold["missing_coords_flag"] = sold["Latitude"].isnull() | sold["Longitude"].isnull()

# coordinates of 0 (a placeholder for unknown)
sold["zero_coords_flag"] = (sold["Latitude"] == 0) | (sold["Longitude"] == 0)

# positive longitude (CA longitudes are negative)
sold["positive_longitude_flag"] = sold["Longitude"] > 0

# outside a rectangle around CA (approximate state boundaries),
# checked only for records that have both coordinates
has_coords = sold["Latitude"].notnull() & sold["Longitude"].notnull()
in_california = (
    sold["Latitude"].between(32.5, 42.1)
    & sold["Longitude"].between(-124.5, -114.0))
sold["out_of_state_flag"] = has_coords & (in_california == False)

# number of records flagged by each check
geo_flags = [
    "missing_coords_flag", "zero_coords_flag",
    "positive_longitude_flag", "out_of_state_flag"]
print(sold[geo_flags].sum())

# %% Cell 9: Save cleaned dataset

print("Rows before cleaning:", rows_start)
print("Rows after cleaning: ", len(sold))
print("Rows removed:        ", rows_start - len(sold))
print("Final rows and columns:", sold.shape)

sold.to_csv(folder + r"\sold_cleaned.csv", index=False)
print("Saved sold_cleaned.csv")