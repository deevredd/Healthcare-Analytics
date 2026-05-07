# ClaimLens NPDB

ClaimLens NPDB is a healthcare analytics dashboard for exploring U.S. medical malpractice payment patterns using the National Practitioner Data Bank Public Use Data File.

The project converts a raw, coded government dataset into an interactive analytics product focused on malpractice allegation types, injury severity, payment concentration, geography, practitioner fields, reporting lag, and data reliability.

## Project Objective

The objective of ClaimLens NPDB is to make public malpractice payment data easier to understand, analyze, and communicate in a responsible healthcare analytics context.

The dashboard helps answer questions such as:

- Which medical malpractice allegation categories account for the highest payment totals?
- How do payment patterns differ across injury severity levels?
- How have report volume and median payment amounts changed over time?
- Which practitioner license fields are associated with the largest payment concentration?
- Which states show higher reported malpractice payment totals?
- How complete and reliable are the fields used in the analysis?

This is not a clinical diagnosis tool, provider ranking system, or negligence detector. It is a healthcare data analytics project built around de-identified public-use malpractice payment records.

## Why This Project Matters

Medical malpractice data is high-stakes, sensitive, and easy to misinterpret. Raw NPDB public-use records are coded, de-identified, and difficult to use directly without understanding the codebook and data limitations.

This project demonstrates how healthcare data should be handled:

- Decode official public-use codes before analysis.
- Separate payment reports from proof of clinical negligence.
- Show data quality instead of hiding missingness.
- Avoid unsupported clinical claims.
- Present findings in a clear, decision-friendly interface.

## Key Features

- **Executive KPI dashboard**: reports, total paid, median payment, P90 payment, and severe injury share.
- **Trend analysis**: yearly report volume and median malpractice payment trends.
- **Payment distribution**: payment-band analysis across filtered records.
- **Injury severity analysis**: NPDB outcome severity mix with median payment context.
- **Allegation intelligence**: ranked allegation categories by total payment, frequency, severity share, and median payment.
- **Geographic analysis**: state-level malpractice payment concentration using available NPDB location fields.
- **Practitioner field analysis**: decoded license/practitioner fields grouped into broader categories.
- **Reliability tab**: field completeness checks for payment, severity, demographics, reporting lag, and location availability.
- **Dark-mode UI**: polished Streamlit dashboard designed for portfolio presentation.

## Dataset

Source: National Practitioner Data Bank Public Use Data File.

Local source file:

```text
data/npdb_public.csv
```

Official code mappings are stored locally in:

```text
data/npdb_codebook.json
```

The codebook JSON was generated from the official NPDB Public Use Data File Format Specifications.

Generated analytics outputs:

```text
data/npdb_analytics.csv
data/data_quality.json
```

## Methodology

The project follows a reproducible analytics workflow:

1. Load the raw NPDB public-use CSV.
2. Decode coded NPDB fields using the official public-use format specification.
3. Clean payment fields and convert dollar strings into numeric amounts.
4. Derive healthcare analytics features, including:
   - report year
   - event year
   - event-to-report lag
   - payment band
   - injury severity score
   - practitioner group
   - state proxy
5. Generate an analytics-ready dataset.
6. Generate a data-quality summary.
7. Render the dashboard with Streamlit and Plotly.

## Tech Stack

- Python
- pandas
- Streamlit
- Plotly
- NPDB Public Use Data File
- Official NPDB format/codebook specifications

## Project Structure

```text
.
├── analyzer.py                 # Aggregation, KPI, trend, and reliability helpers
├── dashboard.py                # Streamlit dashboard
├── pipeline.py                 # Cleaning, decoding, and feature engineering pipeline
├── requirements.txt            # Python dependencies
├── data/
│   ├── npdb_public.csv         # Raw NPDB public-use data
│   ├── npdb_codebook.json      # Official code mappings
│   ├── npdb_analytics.csv      # Generated analytics dataset
│   └── data_quality.json       # Generated data-quality summary
```

## How To Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Build the analytics dataset:

```bash
python3 pipeline.py
```

Launch the dashboard:

```bash
python3 -m streamlit run dashboard.py
```

Then open the local Streamlit URL shown in the terminal.

## Analytical Guardrails

This project is intentionally conservative about what the data can support.

- Malpractice payment reports are not proof of negligence.
- Payment amounts are nominal and not inflation-adjusted.
- The NPDB public-use file is de-identified.
- The project must not be used to identify clinicians, organizations, or patients.
- State is a proxy derived from available work, home, or license state fields.
- Injury severity and patient detail fields are not complete for all historical records.
- The dashboard does not make clinical diagnosis, quality-of-care, or legal liability conclusions.

## What This Project Accomplishes

ClaimLens NPDB turns a raw healthcare/legal public dataset into a structured analytics product. It demonstrates:

- healthcare data cleaning
- codebook-driven feature engineering
- responsible public-data analysis
- dashboard design
- uncertainty and data-quality communication
- domain-aware product thinking

The result is a portfolio-ready healthcare analytics project that is both visually polished and analytically defensible.

## Portfolio Summary

ClaimLens NPDB is a healthcare analytics dashboard that explores U.S. medical malpractice payment patterns using public NPDB data. It focuses on payment concentration, allegation categories, injury severity, geography, reporting lag, practitioner fields, and data reliability while avoiding unsupported clinical or legal claims.

## Possible Future Improvements

- Add inflation-adjusted payment values.
- Add downloadable filtered datasets.
- Add methodology notes inside the dashboard.
- Add state normalization using population or physician workforce counts.
- Add time-series comparisons before and after major reporting format changes.
- Add automated tests for pipeline outputs and field completeness.
