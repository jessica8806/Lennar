---
name: normalize-comps
description: Map uploaded comp report or resale data to the Lennar land acquisition Excel model schema. Use when an analyst uploads a PDF, Excel, CSV, or any external data file containing comparable sales, resales, or land comp data that needs to be ingested into the underwriting model.
allowed-tools: Read, Write, Bash
argument-hint: [file-path] [filters?]
---

# Lennar Data Normalization Agent

You are normalizing external comp or resale data into the Lennar land acquisition underwriting model schema.

## Input

The analyst has provided: $ARGUMENTS

This may be a file path, a description of an uploaded file, or both. If filters were specified (e.g., "built after 2018, lot size min 4000 sqft"), capture those before processing.

---

## Step 1: Collect Filters (if not already provided)

Before normalizing, confirm any filters the analyst wants applied. If filters were specified in $ARGUMENTS, proceed immediately to Step 2.

If $ARGUMENTS contains only a file path with no filter criteria, ask:

- **Built year**: Minimum year built (e.g., 2015 or later)?
- **Lot size**: Min/max square footage?
- **Sale price**: Min/max range?
- **Geography**: Specific zip codes, cities, or radius from a point?
- **Product type**: Any specific home type to include or exclude?

If the analyst says "no filters", proceed immediately to Step 2 with no filtering applied.

---

## Step 2: Read and Inventory the Source File

Read the uploaded file and inventory what you find:

1. List every column/field name present in the source
2. Note the total number of records
3. Flag any immediately obvious data quality issues (blanks, inconsistent formats, outliers)
4. Identify the file format and structure

Output a brief inventory summary before proceeding:

```
Source file:        [filename]
Format:             [PDF / Excel / CSV / other]
Records found:      [N]
Fields found:       [list all column names]
Data quality flags: [any obvious issues]
```

---

## Step 3: Apply Filters

Apply the filters collected in Step 1. Remove records that do not meet the criteria.

Report how many records were retained and how many were filtered out:

```
Records after filtering: [N retained] / [N total]
Filtered out: [N] records
  - Built before [year]:       [N]
  - Lot size out of range:     [N]
  - Price out of range:        [N]
  - Geography exclusion:       [N]
  - Other:                     [N]
```

Save the filtered-out records to a separate tab called `Filtered_Out` in the output file so they can be recovered if needed.

If no filters are specified, skip this step and note "No filters applied" in the Summary tab.

---

## Step 4: Map Fields to Lennar Schema

Load `.claude/lennar-field-schema.md` before mapping. That file contains the canonical Lennar schema fields, required vs. optional status, known synonyms, and formatting rules.

For each mapped field:
- Assign a confidence score: **High** / **Medium** / **Low**
- Note the mapping basis (exact match, synonym match, inferred, or assumed)

For unmapped fields:
- Flag them explicitly — do not silently drop them
- Suggest the most likely Lennar schema field it might correspond to

For Lennar schema fields with no source data:
- Leave the cell blank
- Add the field name to the `Missing_Fields` summary tab

---

## Step 5: Build the Output File

Create a normalized Excel file with the following tabs:

### Tab 1: Normalized_Data

All retained records mapped to the Lennar schema column order (see field schema). Every column header must exactly match a Lennar schema field name.

Formatting rules:
- **Dates**: MM/DD/YYYY
- **Dollar amounts**: No $ symbol, no commas, plain number (e.g., `485000`)
- **Square footage**: Plain integer (e.g., `4200`)
- **Year built**: 4-digit integer (e.g., `2019`)
- **Percentages**: Decimal format (e.g., `0.15` not `15%`)
- **Empty cells**: Leave blank — do not use "N/A" or "—"

### Tab 2: Mapping_Log

A full audit log with one row per field:

| Source Field Name | Lennar Schema Field | Confidence | Mapping Basis | Notes |

Color coding:
- **Green** highlight: High confidence, exact or synonym match
- **Yellow** highlight: Medium confidence, inferred mapping
- **Red** highlight: Low confidence or assumed — requires analyst review

### Tab 3: Missing_Fields

Lennar schema fields that had no corresponding source data:

| Lennar Field | Required? | Suggested Source |

### Tab 4: Filtered_Out

All records removed during filtering, with a column indicating the filter reason. If no records were filtered, include a single row noting "No records filtered."

### Tab 5: Summary

```
Source file:          [filename]
Normalization date:   [today's date MM/DD/YYYY]
Total source records: [N]
Records normalized:   [N]
Records filtered out: [N]
Fields mapped:        [N] / [total Lennar fields]
Fields missing:       [N]
High confidence maps: [N]
Medium confidence:    [N]
Low confidence:       [N]  <- REQUIRE ANALYST REVIEW
Data quality score:   [0-100]
```

**Data quality score formula** (minimum score: 0):
- Start at 100
- Subtract 3 points per missing **required** field
- Subtract 1 point per missing **optional** field
- Subtract 5 points per low-confidence mapping
- Subtract 2 points per medium-confidence mapping

---

## Step 6: Flag for Analyst Review

After delivering the file, explicitly call out anything requiring human judgment:

```
REVIEW REQUIRED BEFORE UNDERWRITING

Low-confidence mappings ([N] fields):
  - [Source field] -> [Lennar field]: [reason for low confidence]

Missing required fields ([N] fields):
  - [Field name]: [suggested data source to fill this]

Data quality score: [N]/100
```

If the data quality score is below 70, add:

```
DATA QUALITY WARNING: Score below 70. Recommend resolving flagged
fields before this data enters the underwriting model.
```

---

## Output File Naming

Name the output file:

```
Lennar_Normalized_[SourceFileName]_[YYYYMMDD].xlsx
```

Save to `land-acquisition/data/normalized/` unless the analyst specifies otherwise.

---

## Supporting Files

- `.claude/lennar-field-schema.md` — Complete field mapping reference. Load this before Step 4.
- `.claude/commands/examples/sample-normalized-output.md` — Example of a correctly normalized output for reference.
