# Sample Normalized Output — Reference Example

This file shows what a correctly normalized output looks like after running `/normalize-comps`. Use it as a reference when validating skill output quality.

**Source file used:** `broker_comp_package.csv` (5 records, filtered to built 2020+, price $400K–$750K)

---

## Tab 1: Normalized_Data

| APN | Street_Address | City | State | Zip_Code | County | Subdivision_Name | Lot_Size_SF | Year_Built | Living_Area_SF | Bedrooms | Bathrooms_Full | Bathrooms_Half | Bathrooms_Total | Garage_Spaces | Stories | Pool | Sale_Price | Sale_Date | Price_Per_SF | Days_On_Market | Builder_Name | Plan_Name | Product_Type | Community_Name | Adjustment_Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 312-18-0042 | 412 Tanglewood Crest Dr | Austin | TX | 78737 | | Belterra | 7200 | 2021 | 3124 | 4 | 3 | 1 | 3.5 | 2 | 2 | N | 589000 | 03/14/2025 | 188.54 | 12 | Meritage Homes | Crestview | SFD | Belterra | Corner lot; upgraded kitchen package |
| 312-18-0091 | 208 Ridgeline Pass | Austin | TX | 78737 | | Belterra | 6800 | 2022 | 3310 | 4 | 3 | 0 | 3.0 | 2 | 2 | N | 625000 | 04/02/2025 | 188.82 | 8 | Highland Homes | The Reserve | SFD | Belterra | Backs to greenbelt |
| 312-19-0017 | 1044 Copper Canyon Ln | Dripping Springs | TX | 78620 | | Headwaters | 8100 | 2020 | 2950 | 3 | 2 | 1 | 2.5 | 2 | 1 | N | 548000 | 02/28/2025 | 185.76 | 21 | Newmark Homes | Juniper | SFD | Headwaters | |
| 312-21-0041 | 2104 Rolling Meadow Trl | Austin | TX | 78748 | | Bear Creek Estates | 6100 | 2021 | 2920 | 4 | 3 | 0 | 3.0 | 2 | 2 | N | 535000 | 03/05/2025 | 183.22 | 14 | Perry Homes | 2500 | SFD | Bear Creek Estates | |
| 312-24-0003 | 701 Crystal Falls Pkwy | Leander | TX | 78641 | | Crystal Falls | 7300 | 2022 | 3400 | 4 | 3 | 1 | 3.5 | 2 | 2 | N | 615000 | 02/22/2025 | 180.88 | 10 | Scott Felder | Presidio | SFD | Crystal Falls | |

**Formatting notes:**
- `State` was not in source — inferred as `TX` from city/zip context (Medium confidence; flagged in Mapping_Log)
- `County` was not in source — left blank
- `Bathrooms_Full` and `Bathrooms_Half` were split from `Baths` decimal field (e.g., 3.5 → Full=3, Half=1)
- `Pool` defaulted to `N` — not present in source (Low confidence; flagged)

---

## Tab 2: Mapping_Log

| Source Field Name | Lennar Schema Field | Confidence | Mapping Basis | Notes |
|---|---|---|---|---|
| Address | Street_Address | High | Synonym match | |
| Parcel Number | APN | High | Synonym match | |
| City | City | High | Exact match | |
| *(not in source)* | State | Medium | Inferred from City/Zip — TX market | Analyst should confirm |
| Zip | Zip_Code | High | Synonym match | |
| Sold Price | Sale_Price | High | Synonym match | |
| Close Date | Sale_Date | High | Synonym match | Reformatted to MM/DD/YYYY |
| Sq Ft | Living_Area_SF | High | Synonym match | |
| Lot SF | Lot_Size_SF | High | Synonym match | |
| Beds | Bedrooms | High | Synonym match | |
| Baths | Bathrooms_Total | High | Synonym match | Split into Full and Half where decimal present |
| Baths (integer part) | Bathrooms_Full | Medium | Calculated from Bathrooms_Total | Full = floor(Baths) |
| Baths (decimal part) | Bathrooms_Half | Medium | Calculated from Bathrooms_Total | Half = 1 if .5, else 0 |
| Yr Built | Year_Built | High | Synonym match | |
| Stories | Stories | High | Exact match | |
| Garage | Garage_Spaces | High | Synonym match | |
| Community | Community_Name | High | Synonym match | Also mapped to Subdivision_Name |
| Builder | Builder_Name | High | Synonym match | |
| Model | Plan_Name | High | Synonym match | |
| Type | Product_Type | High | Synonym match | |
| DOM | Days_On_Market | High | Synonym match | |
| $/SF | Price_Per_SF | High | Synonym match | |
| Notes | Adjustment_Notes | Medium | Synonym match | |
| *(not in source)* | Pool | Low | Assumed N — not in source | Analyst must verify |
| *(not in source)* | County | — | Not in source — left blank | |
| *(not in source)* | APN (row 11) | — | APN missing for 4403 Copper Mesa Dr | Filtered out — see Filtered_Out tab |

---

## Tab 3: Missing_Fields

| Lennar Field | Required? | Suggested Source |
|---|---|---|
| State | Required | Infer from city/zip; confirm with analyst |
| County | Optional | County assessor records; CoStar |
| Lot_Size_Acres | Optional | Calculate: Lot_Size_SF / 43560 |
| Lot_Width_Ft | Optional | Not typically in broker comp packages; pull from plat |
| Lot_Depth_Ft | Optional | Not typically in broker comp packages; pull from plat |
| Corner_Lot | Optional | Partially available in Notes field — not standardized |
| Cul_De_Sac | Optional | Partially available in Notes field — not standardized |
| View | Optional | Partially available in Notes field — not standardized |
| Topography | Optional | Not in source |
| Total_Rooms | Optional | Not in source |
| Garage_Type | Optional | Not in source |
| Foundation | Optional | Not in source |
| Roof_Type | Optional | Not in source |
| Construction_Type | Optional | Not in source |
| Sale_Type | Optional | Assumed Arms Length — not in source |
| Prior_Sale_Price | Optional | Not in source |
| Prior_Sale_Date | Optional | Not in source |
| List_Price | Optional | Not in source |
| Distance_From_Subject_Miles | Optional | Analyst to calculate based on subject parcel |
| Comp_Rank | Optional | Analyst to assign |
| Tract_Number | Optional | Not in source |

---

## Tab 4: Filtered_Out

| APN | Street_Address | City | Filter Reason |
|---|---|---|---|
| 312-21-0009 | 6601 Covered Bridge Dr, Austin | TX | Built before 2020 (Year Built: 2008) |
| *(blank)* | 4403 Copper Mesa Dr, Manor | TX | APN missing — cannot enter model without parcel identifier |

---

## Tab 5: Summary

```
Source file:          broker_comp_package.csv
Normalization date:   03/23/2026
Total source records: 15
Records normalized:   5
Records filtered out: 10
  - Built before 2020:         1
  - Price above $750K:         4
  - Price below $400K:         1
  - Missing APN:               1
  - Outside filter geography:  3
Fields mapped:        21 / 34 total Lennar fields
Fields missing:       13
High confidence maps: 17
Medium confidence:     3
Low confidence:        1  <- REQUIRE ANALYST REVIEW
Data quality score:   72 / 100
```

---

## Analyst Review Flags

```
REVIEW REQUIRED BEFORE UNDERWRITING

Low-confidence mappings (1 field):
  - Pool: Assumed "N" for all records — source did not include pool data.
    Verify against MLS or builder spec sheets before entering model.

Missing required fields (1 field):
  - State: Inferred as TX from city/zip. Confirm this is correct before
    submitting to underwriting model.

Data quality score: 72/100
```

---

## Notes on This Example

This example demonstrates several common scenarios the skill should handle gracefully:

1. **Missing APN** — Record 11 (`4403 Copper Mesa Dr`) had no parcel number. Filtered out and preserved in `Filtered_Out` tab.
2. **Decimal baths** — `Baths` field contained values like `3.5`. Correctly split into `Bathrooms_Full = 3` and `Bathrooms_Half = 1`.
3. **Missing state field** — Source was Texas data but `State` column absent. Inferred as `TX` with Medium confidence.
4. **Seller concession in notes** — Record 5 (`90 Limestone Creek Blvd`) notes a seller concession of $8,500. Preserved in `Adjustment_Notes`. The analyst should consider whether to adjust `Sale_Price` before underwriting.
5. **Older resale filtered** — Record 7 (`6601 Covered Bridge Dr`, built 2008) correctly filtered out when analyst specified "built 2020 or later."
