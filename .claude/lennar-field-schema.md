# Lennar Land Acquisition — Field Schema Reference

This file defines the canonical Lennar underwriting model schema. Use it during Step 4 of the normalization workflow to map source fields to the correct Lennar field names.

-----

## How to Use This File

1. For each source field, scan the **Known Synonyms** column first for an exact or near-exact match
1. If no synonym match, use the **Description** to infer the best mapping
1. Assign confidence: **High** (synonym match), **Medium** (inferred from description), **Low** (assumed or unclear)
1. Never silently drop a source field — always log it in the Mapping_Log even if confidence is Low

-----

## Schema Fields

### Property Identification

|Lennar Field Name |Required|Data Type|Format               |Description                                                         |Known Synonyms                                                                          |
|------------------|--------|---------|---------------------|--------------------------------------------------------------------|----------------------------------------------------------------------------------------|
|`APN`             |Required|Text     |Plain text           |Assessor Parcel Number — unique parcel identifier assigned by county|Parcel Number, Parcel ID, APN Number, Assessor ID, Tax ID, Folio Number, Map Book Parcel|
|`Street_Address`  |Required|Text     |Plain text           |Street address of the property                                      |Address, Property Address, Site Address, Location                                       |
|`City`            |Required|Text     |Plain text           |City name                                                           |Municipality, Jurisdiction, City Name                                                   |
|`State`           |Required|Text     |2-letter abbreviation|State abbreviation                                                  |ST, State Code                                                                          |
|`Zip_Code`        |Required|Text     |5-digit              |ZIP code                                                            |Zip, Postal Code, ZIP                                                                   |
|`County`          |Optional|Text     |Plain text           |County name                                                         |County Name                                                                             |
|`Subdivision_Name`|Optional|Text     |Plain text           |Name of the subdivision or community                                |Sub Name, Plat Name, Community, Development Name, Project Name                          |
|`Tract_Number`    |Optional|Text     |Plain text           |Tract or plat number                                                |Tract, Plat Number, Map Number                                                          |

-----

### Lot & Land Characteristics

|Lennar Field Name|Required|Data Type|Format                  |Description                                                  |Known Synonyms                                                                        |
|-----------------|--------|---------|------------------------|-------------------------------------------------------------|--------------------------------------------------------------------------------------|
|`Lot_Size_SF`    |Required|Integer  |Plain integer, no commas|Lot size in square feet                                      |Lot SF, Lot Square Footage, Land Area SF, Lot Area, Site Size SF, Lot Size (SF), LotSF|
|`Lot_Size_Acres` |Optional|Decimal  |Up to 4 decimal places  |Lot size in acres                                            |Acres, Lot Acres, Land Acres, Site Acres, Lot Size (Acres)                            |
|`Lot_Width_Ft`   |Optional|Integer  |Plain integer           |Width of the lot in feet                                     |Lot Width, Width, Frontage, Lot Frontage                                              |
|`Lot_Depth_Ft`   |Optional|Integer  |Plain integer           |Depth of the lot in feet                                     |Lot Depth, Depth                                                                      |
|`Corner_Lot`     |Optional|Boolean  |Y / N                   |Whether the lot is a corner lot                              |Corner, Is Corner, Corner Flag                                                        |
|`Cul_De_Sac`     |Optional|Boolean  |Y / N                   |Whether the lot is on a cul-de-sac                           |Cul de Sac, CDS, Culdesac                                                             |
|`View`           |Optional|Text     |Plain text              |View type if applicable (e.g., Golf, Mountain, City, None)   |View Type, View Description                                                           |
|`Topography`     |Optional|Text     |Plain text              |General topography description (e.g., Flat, Sloped, Hillside)|Topo, Grade, Slope                                                                    |

-----

### Home Characteristics

|Lennar Field Name  |Required|Data Type|Format             |Description                                  |Known Synonyms                                                                                            |
|-------------------|--------|---------|-------------------|---------------------------------------------|----------------------------------------------------------------------------------------------------------|
|`Year_Built`       |Required|Integer  |4-digit year       |Year the home was originally built           |Yr Built, Build Year, Year of Construction, Built, YrBuilt                                                |
|`Living_Area_SF`   |Required|Integer  |Plain integer      |Conditioned living area in square feet       |Sq Ft, SqFt, GLA, Gross Living Area, Living SF, Home Size, Square Feet, Living Area, Heated SF, Livable SF|
|`Total_Rooms`      |Optional|Integer  |Plain integer      |Total room count                             |Rooms, Room Count                                                                                         |
|`Bedrooms`         |Required|Integer  |Plain integer      |Number of bedrooms                           |Beds, BD, BR, Bed Count, # Bedrooms, Bdrms                                                                |
|`Bathrooms_Full`   |Required|Decimal  |Decimal (e.g., 2.5)|Full bathroom count                          |Full Baths, Baths Full, Full Bath Count                                                                   |
|`Bathrooms_Half`   |Optional|Integer  |Plain integer      |Half bathroom count                          |Half Baths, Powder Rooms, 1/2 Bath                                                                        |
|`Bathrooms_Total`  |Optional|Decimal  |Decimal            |Total bathrooms (full + 0.5 per half)        |Total Baths, Baths, Bath Count, # Baths                                                                   |
|`Garage_Spaces`    |Optional|Integer  |Plain integer      |Number of garage spaces                      |Garage, Garage Cars, Car Garage, Garage Count, Parking Spaces                                             |
|`Garage_Type`      |Optional|Text     |Plain text         |Type of garage (Attached, Detached, None)    |Garage Style, Parking Type                                                                                |
|`Stories`          |Optional|Integer  |Plain integer      |Number of stories                            |Floors, Story Count, # Stories, Levels                                                                    |
|`Pool`             |Optional|Boolean  |Y / N              |Whether the home has a pool                  |Has Pool, Pool Flag, Private Pool                                                                         |
|`Foundation`       |Optional|Text     |Plain text         |Foundation type (Slab, Crawl, Basement)      |Foundation Type                                                                                           |
|`Roof_Type`        |Optional|Text     |Plain text         |Roof material/type                           |Roof, Roof Material                                                                                       |
|`Construction_Type`|Optional|Text     |Plain text         |Construction type (Wood Frame, Masonry, etc.)|Construction, Build Type                                                                                  |

-----

### Sale & Financial Data

|Lennar Field Name |Required|Data Type|Format                       |Description                                      |Known Synonyms                                                                                        |
|------------------|--------|---------|-----------------------------|-------------------------------------------------|------------------------------------------------------------------------------------------------------|
|`Sale_Price`      |Required|Integer  |Plain integer, no $ or commas|Recorded sale price in dollars                   |Sales Price, Sold Price, Closed Price, Close Price, Price, Sale Amount, Transfer Amount, Consideration|
|`Sale_Date`       |Required|Date     |MM/DD/YYYY                   |Date the sale closed/recorded                    |Close Date, Closing Date, Transfer Date, Sold Date, Recording Date, Deed Date                         |
|`Sale_Type`       |Optional|Text     |Plain text                   |Type of sale (Arms Length, REO, Short Sale, etc.)|Transaction Type, Distressed, Sale Classification                                                     |
|`Prior_Sale_Price`|Optional|Integer  |Plain integer                |Previous sale price if available                 |Prior Price, Last Sale Price, Previous Sale                                                           |
|`Prior_Sale_Date` |Optional|Date     |MM/DD/YYYY                   |Date of prior sale                               |Last Sale Date, Previous Sale Date                                                                    |
|`Price_Per_SF`    |Optional|Decimal  |2 decimal places             |Sale price divided by living area SF             |$/SF, Price PSF, Per SF, Dollar Per SF                                                                |
|`Price_Per_Lot_SF`|Optional|Decimal  |2 decimal places             |Sale price divided by lot SF                     |Land $/SF, Price Per Land SF                                                                          |
|`List_Price`      |Optional|Integer  |Plain integer                |Original list price                              |Asking Price, Listed Price, Original Price                                                            |
|`Days_On_Market`  |Optional|Integer  |Plain integer                |Days from list to contract                       |DOM, Days on Market, Marketing Time                                                                   |

-----

### Builder / Developer Data

|Lennar Field Name|Required|Data Type|Format    |Description                                            |Known Synonyms                                           |
|-----------------|--------|---------|----------|-------------------------------------------------------|---------------------------------------------------------|
|`Builder_Name`   |Optional|Text     |Plain text|Name of the builder or developer                       |Builder, Developer, Seller Builder, Homebuilder          |
|`Plan_Name`      |Optional|Text     |Plain text|Floor plan or model name                               |Model, Plan, Floor Plan Name, Model Name                 |
|`Plan_Number`    |Optional|Text     |Plain text|Builder's plan or elevation number                     |Plan #, Model #, Elevation                               |
|`Product_Type`   |Optional|Text     |Plain text|Product type classification (SFD, SFA, Townhome, Condo)|Home Type, Housing Type, Property Type, Attached/Detached|
|`Community_Name` |Optional|Text     |Plain text|Name of the master-planned community                   |MPC, Master Plan, Community                              |

-----

### Comp Analysis Fields

|Lennar Field Name            |Required|Data Type|Format          |Description                                  |Known Synonyms                               |
|-----------------------------|--------|---------|----------------|---------------------------------------------|---------------------------------------------|
|`Distance_From_Subject_Miles`|Optional|Decimal  |2 decimal places|Distance from subject parcel in miles        |Distance, Miles From Subject, Proximity      |
|`Comp_Rank`                  |Optional|Integer  |Plain integer   |Analyst-assigned comp ranking (1 = best comp)|Rank, Comp #, Comparables Rank               |
|`Adjustment_Notes`           |Optional|Text     |Plain text      |Free-text adjustment rationale               |Notes, Adjustments, Comp Notes, Analyst Notes|

-----

## Required Fields Summary

The following fields are **required** for the underwriting model to function. If any of these are missing, flag them as high-priority in the Missing_Fields tab:

1. `APN`
1. `Street_Address`
1. `City`
1. `State`
1. `Zip_Code`
1. `Lot_Size_SF`
1. `Year_Built`
1. `Living_Area_SF`
1. `Bedrooms`
1. `Bathrooms_Full`
1. `Sale_Price`
1. `Sale_Date`

-----

## Common Mapping Ambiguities

These situations come up frequently. Use this guidance when confidence is unclear:

**"Baths" with a decimal (e.g., 2.5)** → Map to `Bathrooms_Total`. Do not split unless full and half are provided separately.

**"Square Feet" without clarification** → Assume `Living_Area_SF` unless context indicates lot size (e.g., in a land-only comp file).

**"Price" without context** → Assume `Sale_Price` if there is a corresponding date field. Flag as Medium confidence.

**"Type" without clarification** → Could be `Sale_Type`, `Product_Type`, `Garage_Type`, or `Construction_Type`. Flag as Low confidence and ask analyst.

**"Date" without clarification** → Assume `Sale_Date` if it is the only date field. Flag as Medium confidence.

**"Notes" or "Comments"** → Map to `Adjustment_Notes`. Flag as Medium confidence.

**Lot size in acres only** → Map to `Lot_Size_Acres` and calculate `Lot_Size_SF` (multiply by 43,560). Note the calculation in the Mapping_Log.

**"DOM" or "Days"** → Map to `Days_On_Market`.

-----

## Fields to Never Invent

If the following fields are not present in the source data, leave them blank. Do **not** calculate or assume values for these:

- `Sale_Price` — never estimate
- `Sale_Date` — never estimate
- `APN` — never estimate
- `Year_Built` — never estimate
- `Living_Area_SF` — never estimate from other fields unless explicitly instructed

-----

## Placeholder for Lennar-Specific Additions

> **Note for Jessica / Lennar team:** The fields above represent a strong baseline schema derived from standard homebuilder comp analysis practice. Before deploying this skill, validate and extend this schema with:
>
> 1. Any Lennar-specific fields not listed above (e.g., internal deal codes, division codes, underwriter IDs)
> 1. The exact column order the Excel model expects (order matters for paste-compatibility)
> 1. Any calculated fields the model derives from raw inputs (e.g., Price_Per_SF may be auto-calculated in the model — if so, mark it as do-not-populate)
> 1. Specific data sources the land team uses (CoStar, Metrostudy, MLS, broker packages) so synonyms can be expanded based on those sources' actual field names
>
> Replace this section with confirmed schema details after the discovery session with the Lennar land team.
