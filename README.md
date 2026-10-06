# IDX Exchange Data Analyst Internship

Weekly deliverables for the IDX Exchange Data Analyst internship.

## Week 1: Monthly Dataset Aggregation

**Script:** `IDXweek1_aggregate.py`

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

The MLS data files are confidential and not included in this repository.

## Weeks 2-3: Dataset Structuring and Validation (Sold)

**Script:** `IDXweek2_sold_eda.py`

Inspects the combined sold dataset, documents property types, filters to
Residential, reports missing values, and summarizes key numeric fields.
Saves the filtered dataset as `sold_residential_validated.csv`.

Last run: 10/5/2026

### Dataset structure

- 33 monthly files, 736,333 rows and 84 columns before filtering
- Date fields (`CloseDate`, `ListingContractDate`, `PurchaseContractDate`,
  `ContractStatusChangeDate`) are stored as text and will need converting
- `latfilled` and `lonfilled` are not standard MLS fields (pending for later)

### Property types and filter

| Property type       | Rows    | Share  |
|---------------------|---------|--------|
| Residential         | 495,195 | 67.25% |
| ResidentialLease    | 169,422 | 23.01% |
| Land                | 23,303  | 3.16%  |
| ResidentialIncome   | 19,786  | 2.69%  |
| ManufacturedInPark  | 19,762  | 2.68%  |
| CommercialSale      | 4,558   | 0.62%  |
| CommercialLease     | 3,833   | 0.52%  |
| BusinessOpportunity | 474     | 0.06%  |

Filtering logic: `sold = sold[sold.PropertyType == 'Residential']`

| | Rows |
|---|---|
| Before filter | 736,333 |
| After filter  | 495,195 |
| Removed       | 241,138 |

### Missing value report

15 columns are above 90% missing:

- **100% missing:** TaxYear, FireplacesTotal, TaxAnnualAmount,
  AboveGradeFinishedArea, ElementarySchoolDistrict, BusinessType,
  CoveredSpaces, MiddleOrJuniorSchoolDistrict
- **90-99.9% missing:** WaterfrontYN (99.94), BelowGradeFinishedArea (99.39),
  BasementYN (98.04), BuilderName (95.14), LotSizeDimensions (95.12),
  BuildingAreaTotal (92.98), CoBuyerAgentFirstName (90.79)

Decision: dropped all 15 (none are core analysis fields). Columns went from
84 to 69, with rows unchanged at 495,195.

Key fields are nearly complete: ClosePrice (2 rows missing), ListPrice (0),
DaysOnMarket (0), CloseDate (0), LivingArea (0.06%), YearBuilt (0.09%),
Latitude/Longitude (0.97%), LotSizeAcres (7.67%).

### Numeric distribution summary

| Field                 | Min  | 1%      | 25%     | Median  | Mean      | 75%       | 99%       | Max           |
|-----------------------|------|---------|---------|---------|-----------|-----------|-----------|---------------|
| ClosePrice            | 0    | 200,000 | 575,000 | 825,000 | 1,189,657 | 1,300,000 | 5,600,000 | 989,500,000   |
| LivingArea            | 0    | 606     | 1,250   | 1,648   | 1,903     | 2,227     | 5,300     | 17,021,321    |
| DaysOnMarket          | -288 | 0       | 8       | 19      | 38        | 49        | 235       | 12,430        |
| ListPrice             | 1    | 210,000 | 575,000 | 819,000 | 1,145,011 | 1,295,000 | 5,795,000 | 170,000,000   |
| OriginalListPrice     | 0    | 210,000 | 585,000 | 829,000 | 1,227,971 | 1,299,000 | 5,995,000 | 1,390,000,000 |
| LotSizeAcres          | 0    | 0.00    | 0.12    | 0.17    | 58.32     | 0.28      | 10.99     | 7,810,698     |
| BedroomsTotal         | 0    | 1       | 3       | 3       | 3.21      | 4         | 6         | 45            |
| BathroomsTotalInteger | 0    | 1       | 2       | 2       | 2.54      | 3         | 6         | 175           |
| YearBuilt             | 1776 | 1912    | 1960    | 1979    | 1979      | 1999      | 2025      | 2027          |

The first three rows are the deliverable fields. ClosePrice and DaysOnMarket
are right-skewed (mean is higher than median). ClosePrice peaks around
600,000-800,000 and DaysOnMarket peaks at 5-10 days.

### Extreme outliers identified (to handle in later weeks)

- ClosePrice: 0, and values up to 989.5 million
- LivingArea: 0, and up to ~17 million sq ft
- DaysOnMarket: negative values (min -288), and up to 12,430
- ListPrice: as low as 1, and up to 170 million
- OriginalListPrice: 0, and up to 1.39 billion
- LotSizeAcres: up to 7.8 million (mean 58.32 vs. median 0.17)
- BedroomsTotal: 0, and up to 45
- BathroomsTotalInteger: 0, and up to 175
- YearBuilt: as early as 1776, and as late as 2027

The 1st-99th percentile range is plausible for all nine fields.

### Suggested question responses

- **Residential share:** 67.25% of all sold records
- **Median and average close price:** 825,000 and 1,189,657
- **Days on Market:** right-skewed, median 19 days, 75% sold within 49 days
- **Sold above vs. below list price:** 39.62% above, 42.93% below,
  17.44% at list price
- **Close date before listing date:** 75 rows (to handle in later weeks)
- **Highest median price counties:** San Mateo (1,700,000),
  Santa Clara (1,590,000), San Francisco (1,200,000),
  Santa Cruz (1,188,000), Orange (1,185,000). Del Norte, Alpine, and
  Other County also rank in the top 10 but have only 1-5 sales each,
  so their medians are not very reliable.

### Market analysis fields vs. metadata fields

Classified by whether a field can be grouped, averaged, or counted for
market analysis, or only identifies/tracks a record. Covers the 69 columns
remaining after the drop.

**Market analysis fields (55)**

- **Price:** ClosePrice, ListPrice, OriginalListPrice
- **Dates and timing:** CloseDate, ListingContractDate,
  PurchaseContractDate, ContractStatusChangeDate, DaysOnMarket
- **Property type and status:** PropertyType, PropertySubType, MlsStatus
- **Size and features:** LivingArea, LotSizeAcres, LotSizeSquareFeet,
  LotSizeArea, BedroomsTotal, BathroomsTotalInteger, MainLevelBedrooms,
  YearBuilt, Stories, Levels, GarageSpaces, ParkingTotal, AttachedGarageYN,
  FireplaceYN, PoolPrivateYN, ViewYN, NewConstructionYN, Flooring
- **Location:** CountyOrParish, City, PostalCode, StateOrProvince,
  MLSAreaMajor, SubdivisionName, Latitude, Longitude, ElementarySchool,
  MiddleOrJuniorSchool, HighSchool, HighSchoolDistrict
- **Fees:** AssociationFee, AssociationFeeFrequency
- **Agents and offices:** ListAgentFullName, ListAgentFirstName,
  ListAgentLastName, ListOfficeName, CoListAgentFirstName,
  CoListAgentLastName, CoListOfficeName, BuyerAgentFirstName,
  BuyerAgentLastName, BuyerOfficeName, BuyerAgencyCompensation,
  BuyerAgencyCompensationType

**Metadata fields (14)**

- **Record and property identifiers:** ListingKey (primary key),
  ListingKeyNumeric, ListingId, UnparsedAddress, StreetNumberNumeric
- **Agent, office, and system identifiers:** BuyerAgentMlsId,
  ListAgentEmail, ListAgentAOR, BuyerAgentAOR, BuyerOfficeAOR,
  OriginatingSystemName, OriginatingSystemSubName
- **Data pipeline flags:** latfilled, lonfilled

### Still to do for Weeks 2-3

- Repeat this validation for the listings dataset
- Mortgage rate enrichment
