# -*- coding: utf-8 -*-
"""
IDX Exchange Internship - Week 6: Feature Engineering and Market Metrics
Dataset: Sold transactions (January 2024 - September 2026)

@author: Emma

Creates market metrics from the cleaned sold dataset: price ratios, price
per square foot, time fields, and timeline durations. Summarizes the
metrics by county and property subtype and saves the dataset as a new CSV.

Run the cells in order.
"""

# %% Cell 1: Load the cleaned sold dataset

import pandas as pd

folder = r"C:\Users\Emma\MY_IDX_FILES\csv"

sold = pd.read_csv(folder + r"\sold_cleaned.csv", low_memory=False)
print("Rows and columns:", sold.shape)

# %% Cell 2: Convert date fields to datetime

# csv files store dates as text so they are converted again after loading
date_fields = ["CloseDate", "PurchaseContractDate", "ListingContractDate"]
for col in date_fields:
    sold[col] = pd.to_datetime(sold[col], errors="coerce")

print(sold[date_fields].dtypes)

# %% Cell 3: Price metrics

# price ratio: close price vs. final list price (negotiation strength)
sold["price_ratio"] = sold["ClosePrice"] / sold["ListPrice"]

# close to original list ratio: close price vs. first list price
# (an original list price of 0 cannot be divided by so its treated as missing)
print("OriginalListPrice of 0:", (sold["OriginalListPrice"] == 0).sum())
original_list = sold["OriginalListPrice"].where(sold["OriginalListPrice"] > 0)
sold["close_to_original_list_ratio"] = sold["ClosePrice"] / original_list

# price per square foot (missing where LivingArea is missing)
sold["price_per_sqft"] = sold["ClosePrice"] / sold["LivingArea"]

# %% Cell 4: Time fields

# year and month of the sale, from CloseDate
sold["close_year"] = sold["CloseDate"].dt.year
sold["close_month"] = sold["CloseDate"].dt.month

# YrMo, rebuilt from CloseDate (replaces the text version saved in week 3)
sold["year_month"] = sold["CloseDate"].dt.to_period("M")

print(sold[["CloseDate", "close_year", "close_month", "year_month"]].head())

# %% Cell 5: Timeline durations

# days from listing to accepted offer
sold["listing_to_contract_days"] = (
    sold["PurchaseContractDate"] - sold["ListingContractDate"]).dt.days

# days from accepted offer to close (escrow)
sold["contract_to_close_days"] = (
    sold["CloseDate"] - sold["PurchaseContractDate"]).dt.days

# negative durations should match the date flags from Weeks 4-5
print("Negative listing to contract days:", (sold["listing_to_contract_days"] < 0).sum())
print("negative_timeline_flag:           ", sold["negative_timeline_flag"].sum())
print("Negative contract to close days:  ", (sold["contract_to_close_days"] < 0).sum())
print("purchase_after_close_flag:        ", sold["purchase_after_close_flag"].sum())

# %% Cell 6: Sample of the new columns

# display settings so wide tables print in full with readable numbers
pd.set_option("display.float_format", "{:,.2f}".format)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

metric_cols = [
    "price_ratio", "close_to_original_list_ratio", "price_per_sqft",
    "DaysOnMarket", "listing_to_contract_days", "contract_to_close_days"]

# sample rows showing the new columns populated
print(sold[["year_month"] + metric_cols].head(10))

# median and middle-half range of each metric
print(sold[metric_cols].describe(percentiles=[0.25, 0.50, 0.75]))

# %% Cell 7: Segment summaries

# metrics by county (top 10 by number of sales)
county_summary = sold.groupby("CountyOrParish").agg(
    sales=("ClosePrice", "count"),
    median_price=("ClosePrice", "median"),
    median_price_per_sqft=("price_per_sqft", "median"),
    median_days_on_market=("DaysOnMarket", "median"),
    median_price_ratio=("price_ratio", "median"))
print(county_summary.sort_values("sales", ascending=False).head(10))

# metrics by property subtype (PropertyType is Residential for every row)
subtype_summary = sold.groupby("PropertySubType").agg(
    sales=("ClosePrice", "count"),
    median_price=("ClosePrice", "median"),
    median_price_per_sqft=("price_per_sqft", "median"),
    median_days_on_market=("DaysOnMarket", "median"),
    median_price_ratio=("price_ratio", "median"))
print(subtype_summary.sort_values("sales", ascending=False))

# %% Cell 8: Save the dataset with metrics

print("Final rows and columns:", sold.shape)

sold.to_csv(folder + r"\sold_metrics.csv", index=False)
print("Saved sold_metrics.csv")
