import json
from pathlib import Path

import pandas as pd


RAW_PATH = Path("data/npdb_public.csv")
CODEBOOK_PATH = Path("data/npdb_codebook.json")
ANALYTICS_PATH = Path("data/npdb_analytics.csv")
QUALITY_PATH = Path("data/data_quality.json")


PHYSICIAN_CODES = {10, 15, 20, 25}
DENTIST_CODES = {30, 35}
NURSE_CODES = {100, 110, 120, 130, 134, 135, 140, 141, 142}

OUTCOME_SEVERITY_SCORE = {
    1: 1,
    2: 2,
    3: 3,
    4: 4,
    5: 5,
    6: 6,
    7: 7,
    8: 8,
    9: 9,
    10: 10,
}


def money_to_number(series: pd.Series) -> pd.Series:
    return pd.to_numeric(
        series.astype(str).str.replace(r"[$,]", "", regex=True).replace({"nan": None, "": None}),
        errors="coerce",
    )


def load_codebook() -> dict:
    if not CODEBOOK_PATH.exists():
        raise FileNotFoundError(
            "Missing data/npdb_codebook.json. Generate it from the official NPDB format "
            "specification before running the pipeline."
        )
    return json.loads(CODEBOOK_PATH.read_text(encoding="utf-8"))


def code_key(value):
    if pd.isna(value):
        return None
    try:
        numeric = float(value)
        if numeric.is_integer():
            return str(int(numeric))
    except (TypeError, ValueError):
        pass
    return str(value).strip()


def decode(series: pd.Series, mapping: dict, missing_label: str = "Not reported") -> pd.Series:
    return series.map(lambda value: mapping.get(code_key(value), missing_label))


def profession_group(code) -> str:
    key = code_key(code)
    if key is None:
        return "Unknown"
    value = int(float(key))
    if value in PHYSICIAN_CODES:
        return "Physician"
    if value in DENTIST_CODES:
        return "Dentist"
    if value in NURSE_CODES:
        return "Nurse"
    if value >= 1300:
        return "Organization"
    return "Other licensed practitioner"


def payment_band(amount) -> str:
    if pd.isna(amount):
        return "Not reported"
    if amount < 10_000:
        return "< $10k"
    if amount < 50_000:
        return "$10k-$49k"
    if amount < 100_000:
        return "$50k-$99k"
    if amount < 250_000:
        return "$100k-$249k"
    if amount < 500_000:
        return "$250k-$499k"
    if amount < 1_000_000:
        return "$500k-$999k"
    return "$1M+"


def clean_year(series: pd.Series, low: int = 1900, high: int = 2026) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce")
    return values.where(values.between(low, high))


def build_dataset() -> pd.DataFrame:
    raw = pd.read_csv(RAW_PATH)
    codebook = load_codebook()

    df = raw.copy()
    df["payment_amount"] = money_to_number(df["PAYMENT"])
    df["total_payment_amount"] = money_to_number(df["TOTALPMT"])
    df["report_year"] = clean_year(df["ORIGYEAR"], 1990, 2026)
    df["event_year"] = clean_year(df["MALYEAR1"], 1900, 2026)
    df["event_to_report_years"] = df["report_year"] - df["event_year"]
    df["event_to_report_years"] = df["event_to_report_years"].where(df["event_to_report_years"].between(0, 80))
    df["state"] = df["WORKSTAT"].fillna(df["HOMESTAT"]).fillna(df["LICNSTAT"])

    for column in [
        "RECTYPE",
        "REPTYPE",
        "LICNFELD",
        "ALGNNATR",
        "ALEGATN1",
        "ALEGATN2",
        "OUTCOME",
        "PRACTAGE",
        "PTAGE",
        "PTSEX",
        "PTTYPE",
        "PAYTYPE",
        "PAYNUMBR",
        "PYRRLTNS",
        "WORKSTAT",
    ]:
        df[f"{column.lower()}_label"] = decode(df[column], codebook.get(column, {}))

    df["profession_group"] = df["LICNFELD"].map(profession_group)
    df["outcome_score"] = pd.to_numeric(df["OUTCOME"], errors="coerce").map(OUTCOME_SEVERITY_SCORE)
    df["payment_band"] = df["payment_amount"].map(payment_band)
    df["has_patient_detail"] = df[["PTAGE", "PTSEX", "PTTYPE"]].notna().all(axis=1)
    df["has_severity"] = df["OUTCOME"].notna()
    df["has_secondary_allegation"] = df["ALEGATN2"].notna()

    output_columns = [
        "SEQNO",
        "report_year",
        "event_year",
        "event_to_report_years",
        "state",
        "rectype_label",
        "reptype_label",
        "profession_group",
        "licnfeld_label",
        "algnnatr_label",
        "alegatn1_label",
        "alegatn2_label",
        "outcome_label",
        "outcome_score",
        "payment_amount",
        "total_payment_amount",
        "payment_band",
        "practage_label",
        "ptage_label",
        "ptsex_label",
        "pttype_label",
        "paytype_label",
        "paynumbr_label",
        "pyrrltns_label",
        "NPMALRPT",
        "has_patient_detail",
        "has_severity",
        "has_secondary_allegation",
    ]
    analytics = df[output_columns].copy()
    analytics.to_csv(ANALYTICS_PATH, index=False)

    quality = {
        "source_rows": int(len(raw)),
        "analytics_rows": int(len(analytics)),
        "report_year_min": int(analytics["report_year"].min()),
        "report_year_max": int(analytics["report_year"].max()),
        "payment_complete_pct": round(float(analytics["payment_amount"].notna().mean() * 100), 1),
        "severity_complete_pct": round(float(analytics["has_severity"].mean() * 100), 1),
        "patient_detail_complete_pct": round(float(analytics["has_patient_detail"].mean() * 100), 1),
        "event_year_complete_pct": round(float(analytics["event_year"].notna().mean() * 100), 1),
        "report_lag_complete_pct": round(float(analytics["event_to_report_years"].notna().mean() * 100), 1),
        "work_state_complete_pct": round(float(raw["WORKSTAT"].notna().mean() * 100), 1),
        "codebook_source": "NPDB Public Use Data File Format Specifications",
    }
    QUALITY_PATH.write_text(json.dumps(quality, indent=2), encoding="utf-8")
    return analytics


if __name__ == "__main__":
    dataset = build_dataset()
    print(f"Wrote {ANALYTICS_PATH} with {len(dataset):,} records")
    print(f"Wrote {QUALITY_PATH}")
