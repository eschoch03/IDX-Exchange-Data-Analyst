# -*- coding: utf-8 -*-
"""
IDX Exchange Internship - Week 7: Outlier Detection and Data Quality
Dataset: Sold transactions (January 2024 - September 2026)

@author: Emma

Applies the IQR method to ClosePrice, LivingArea, and DaysOnMarket, adds
outlier flag columns, and saves both a full flagged dataset and a filtered
analysis dataset. Compares dataset size and medians before and after.

The script is organized in cells that follow the handbook sections.
Run the cells in order.
"""

# %% Cell 1: Load the sold dataset with metrics

import pandas as pd

folder = r"C:\Users\Emma\MY_IDX_FILES\csv"

sold = pd.read_csv(folder + r"\sold_metrics.csv", low_memory=False)
print("Rows and columns:", sold.shape)

# %% Cell 2: IQR outlier flags

iqr_fields = ["ClosePrice", "LivingArea", "DaysOnMarket"]

for field in iqr_fields:
    Q1 = sold[field].quantile(0.25)
    Q3 = sold[field].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR

    # flag values outside the IQR range (missing values are not flagged)
    flag_col = field + "_outlier_flag"
    sold[flag_col] = (sold[field] < lower) | (sold[field] > upper)

    # IQR range shown alongside the 1st-99th percentile range for comparison
    print(field)
    print("  IQR range:           ", round(lower, 2), "to", round(upper, 2))
    print("  1st-99th percentile: ", round(sold[field].quantile(0.01), 2),
          "to", round(sold[field].quantile(0.99), 2))
    print("  records flagged:     ", sold[flag_col].sum())

# %% Cell 3: Combined outlier flag

# a record is an outlier if any of the three fields is flagged
sold["any_outlier_flag"] = (
    sold["ClosePrice_outlier_flag"]
    | sold["LivingArea_outlier_flag"]
    | sold["DaysOnMarket_outlier_flag"])

flagged = sold["any_outlier_flag"].sum()
print("Records flagged in any field:", flagged)
print("Share of all records (%):", round(flagged / len(sold) * 100, 2))

# %% Cell 4: Filtered analysis dataset

# the filtered dataset keeps only records with no outlier flags; the full
# dataset keeps every record so nothing is permanently deleted
sold_filtered = sold[sold["any_outlier_flag"] == False]

print("Rows in full dataset:    ", len(sold))
print("Rows in filtered dataset:", len(sold_filtered))
print("Rows filtered out:       ", len(sold) - len(sold_filtered))

# %% Cell 5: Before and after comparison

# display settings so tables print with readable numbers
pd.set_option("display.float_format", "{:,.2f}".format)

compare_fields = [
    "ClosePrice", "LivingArea", "DaysOnMarket",
    "price_per_sqft", "price_ratio"]

# median of each field before and after filtering
comparison = pd.DataFrame({
    "median_before": sold[compare_fields].median(),
    "median_after": sold_filtered[compare_fields].median()})

comparison["change_pct"] = (
    (comparison["median_after"] - comparison["median_before"])
    / comparison["median_before"] * 100)

print(comparison)

# %% Cell 6: Save both datasets

sold.to_csv(folder + r"\sold_flagged.csv", index=False)
print("Saved sold_flagged.csv:", sold.shape)

sold_filtered.to_csv(folder + r"\sold_filtered.csv", index=False)
print("Saved sold_filtered.csv:", sold_filtered.shape)
