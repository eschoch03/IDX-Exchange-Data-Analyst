# IDX Exchange Data Analyst Internship

Weekly deliverables for the IDX Exchange MLS analytics internship.

## Week 1: Monthly Dataset Aggregation

**Script:** `IDX_Workspace_Emma.py`

Combines monthly CRMLS files into two datasets with one for sold properties
and one for listings (spans January 2024 - September 2026).

### Script Function

1. Finds all monthly Sold and Listing CSV files in the data folder
2. Reads each file and prints its row count
3. Concatenates the monthly files into one dataset per type
4. Filters each dataset to `PropertyType == 'Residential'`
5. Saves the results as two new CSV files

### Results

| Dataset  | Monthly files | Rows after concat | Rows after Residential filter |
|----------|---------------|-------------------|-------------------------------|
| Sold     | 33            | 736,333           | 495,195                       |
| Listings | 33            | 1,046,356         | 665,393                       |

Row counts before and after concatenation matched for both datasets.

### Note:

The MLS data files are confidential and are not included in this repository.
