# -*- coding: utf-8 -*-
"""
IDX Exchange Internship - Weeks 4-5: Data Cleaning and Preparation
Dataset: Listings (January 2024 - September 2026)

@author: Emma

Cleans the enriched listings dataset  (removes duplicate columns, converts
date fields, removes redundant columns, handles missing and invalid values,
flags date and geographic issues, and saves a CSV).

Script is organized in cells that follow the handbook sections.
Run the cells in order.
"""

# %% Cell 1: Load the enriched listings dataset

import pandas as pd

folder = r"C:\Users\Emma\MY_IDX_FILES\csv"

listings = pd.read_csv(folder + r"\listings_with_rates.csv", low_memory=False)

rows_start = len(listings)
print("Rows and columns:", listings.shape)

# %% Cell 2: Remove duplicate columns

# 11 fields are requested twice by the extraction script, so a second copy
# was loaded with a ".1" suffix (e.g., PropertyType.1)
duplicate_cols = []
for col in listings.columns:
    if col.endswith(".1"):
        duplicate_cols.append(col)

# confirm each copy matches its original before removing it
for col in duplicate_cols:
    original = col.replace(".1", "")
    print(col, "matches", original + ":", listings[col].equals(listings[original]))

print("Shape before removing duplicates:", listings.shape)
listings = listings.drop(columns=duplicate_cols)
print("Shape after removing duplicates: ", listings.shape)

# %% Cell 3: Convert date fields to datetime

date_fields = [
    "CloseDate", "PurchaseContractDate",
    "ListingContractDate", "ContractStatusChangeDate"]

# data types before conversion (stored as text)
print(listings[date_fields].dtypes)

# convert each field (values that cannot be read as a date become missing)
for col in date_fields:
    filled_before = listings[col].notnull().sum()
    listings[col] = pd.to_datetime(listings[col], errors="coerce")
    filled_after = listings[col].notnull().sum()
    print(col, "- unreadable dates set to missing:", filled_before - filled_after)

# data types after conversion
print(listings[date_fields].dtypes)

# %% Cell 4: Remove redundant/unnecessary columns

# redundant (same info is in another column)
redundant_cols = [
    "ListingKeyNumeric",                        # exact copy of ListingKey
    "ListAgentFirstName", "ListAgentLastName",  # combined in ListAgentFullName
    "LotSizeSquareFeet",                        # same as LotSizeAcres
    "LotSizeArea"]                              # mixed units (not reliable)

# unnecessary (metadata not used for analysis)
metadata_cols = ["ListAgentEmail", "BuyerAgentMlsId", "BuyerOfficeAOR"]

print("Shape before removing columns:", listings.shape)
listings = listings.drop(columns=redundant_cols + metadata_cols)
print("Shape after removing columns: ", listings.shape)

# %% Cell 5: Handle missing values

# no rows are removed: a listing without a close price has not sold yet,
# and the core listing fields (ListPrice, ListingContractDate) are complete

# missing values are left blank: they mostly mean the field does not
# apply or wasnt provided, and filling them in would invent data
print(listings.isnull().sum().sort_values(ascending=False).head(15))

# %% Cell 6: Confirm numeric field types

numeric_fields = [
    "ClosePrice", "ListPrice", "OriginalListPrice", "LivingArea",
    "LotSizeAcres", "BedroomsTotal", "BathroomsTotalInteger",
    "DaysOnMarket", "YearBuilt", "rate_30yr_fixed"]

print(listings[numeric_fields].dtypes)

# %% Cell 7: Invalid numeric values

# count records that break handbook's validity rules
print("ClosePrice <= 0:", (listings["ClosePrice"] <= 0).sum())
print("LivingArea <= 0:", (listings["LivingArea"] <= 0).sum())
print("DaysOnMarket < 0:", (listings["DaysOnMarket"] < 0).sum())
print("BedroomsTotal < 0:", (listings["BedroomsTotal"] < 0).sum())
print("BathroomsTotalInteger < 0:", (listings["BathroomsTotalInteger"] < 0).sum())

# ClosePrice <= 0, LivingArea <= 0 and DaysOnMarket < 0: the listing is
# still valid, so only the invalid value is set to missing
listings["ClosePrice"] = listings["ClosePrice"].where(listings["ClosePrice"] > 0)
listings["LivingArea"] = listings["LivingArea"].where(listings["LivingArea"] > 0)
listings["DaysOnMarket"] = listings["DaysOnMarket"].where(listings["DaysOnMarket"] >= 0)

# %% Cell 8: Date consistency flags

# expected order: ListingContractDate, then PurchaseContractDate, then CloseDate
listings["listing_after_close_flag"] = listings["ListingContractDate"] > listings["CloseDate"]
listings["purchase_after_close_flag"] = listings["PurchaseContractDate"] > listings["CloseDate"]
listings["negative_timeline_flag"] = listings["PurchaseContractDate"] < listings["ListingContractDate"]

# number of records flagged by each check
flag_cols = [
    "listing_after_close_flag", "purchase_after_close_flag",
    "negative_timeline_flag"]
print(listings[flag_cols].sum())

# %% Cell 9: Geographic data checks

# missing coordinates
listings["missing_coords_flag"] = listings["Latitude"].isnull() | listings["Longitude"].isnull()

# coordinates of 0 (a placeholder for unknown)
listings["zero_coords_flag"] = (listings["Latitude"] == 0) | (listings["Longitude"] == 0)

# positive longitude (CA longitudes are negative)
listings["positive_longitude_flag"] = listings["Longitude"] > 0

# outside a rectangle around CA (approximate state boundaries),
# checked only for records that have both coordinates
has_coords = listings["Latitude"].notnull() & listings["Longitude"].notnull()
in_california = (
    listings["Latitude"].between(32.5, 42.1)
    & listings["Longitude"].between(-124.5, -114.0))
listings["out_of_state_flag"] = has_coords & (in_california == False)

# number of records flagged by each check
geo_flags = [
    "missing_coords_flag", "zero_coords_flag",
    "positive_longitude_flag", "out_of_state_flag"]
print(listings[geo_flags].sum())

# %% Cell 10: Save cleaned dataset

print("Rows before cleaning:", rows_start)
print("Rows after cleaning: ", len(listings))
print("Rows removed:        ", rows_start - len(listings))
print("Final rows and columns:", listings.shape)

listings.to_csv(folder + r"\listings_cleaned.csv", index=False)
print("Saved listings_cleaned.csv")
