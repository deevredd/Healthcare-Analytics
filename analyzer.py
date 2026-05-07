import pandas as pd


def filtered_frame(df: pd.DataFrame, years: tuple[int, int], states: list[str], groups: list[str]) -> pd.DataFrame:
    out = df[df["report_year"].between(years[0], years[1])].copy()
    if states:
        out = out[out["state"].isin(states)]
    if groups:
        out = out[out["profession_group"].isin(groups)]
    return out


def kpis(df: pd.DataFrame) -> dict:
    payment = df["payment_amount"]
    return {
        "reports": len(df),
        "total_paid": payment.sum(),
        "median_payment": payment.median(),
        "p90_payment": payment.quantile(0.9),
        "severe_share": (df["outcome_score"].fillna(0) >= 6).mean() * 100 if len(df) else 0,
        "median_report_lag": df["event_to_report_years"].median(),
    }


def yearly_trends(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("report_year", dropna=False)
        .agg(
            reports=("SEQNO", "count"),
            total_paid=("payment_amount", "sum"),
            median_payment=("payment_amount", "median"),
            severe_share=("outcome_score", lambda s: (s.fillna(0) >= 6).mean() * 100),
            median_report_lag=("event_to_report_years", "median"),
        )
        .reset_index()
        .sort_values("report_year")
    )


def allegation_summary(df: pd.DataFrame, min_cases: int = 25) -> pd.DataFrame:
    grouped = (
        df.groupby(["algnnatr_label", "alegatn1_label"], dropna=False)
        .agg(
            reports=("SEQNO", "count"),
            total_paid=("payment_amount", "sum"),
            median_payment=("payment_amount", "median"),
            severe_share=("outcome_score", lambda s: (s.fillna(0) >= 6).mean() * 100),
            median_report_lag=("event_to_report_years", "median"),
        )
        .reset_index()
    )
    return grouped[grouped["reports"] >= min_cases].sort_values(["total_paid", "reports"], ascending=False)


def profession_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["profession_group", "licnfeld_label"], dropna=False)
        .agg(
            reports=("SEQNO", "count"),
            total_paid=("payment_amount", "sum"),
            median_payment=("payment_amount", "median"),
            severe_share=("outcome_score", lambda s: (s.fillna(0) >= 6).mean() * 100),
        )
        .reset_index()
        .sort_values("total_paid", ascending=False)
    )


def state_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.dropna(subset=["state"])
        .groupby("state")
        .agg(
            reports=("SEQNO", "count"),
            total_paid=("payment_amount", "sum"),
            median_payment=("payment_amount", "median"),
            severe_share=("outcome_score", lambda s: (s.fillna(0) >= 6).mean() * 100),
        )
        .reset_index()
    )


def severity_mix(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["outcome_score", "outcome_label"], dropna=False)
        .agg(reports=("SEQNO", "count"), median_payment=("payment_amount", "median"))
        .reset_index()
        .sort_values("outcome_score")
    )


def payment_distribution(df: pd.DataFrame) -> pd.DataFrame:
    order = ["< $10k", "$10k-$49k", "$50k-$99k", "$100k-$249k", "$250k-$499k", "$500k-$999k", "$1M+"]
    out = df.groupby("payment_band").agg(reports=("SEQNO", "count")).reindex(order).reset_index()
    out["reports"] = out["reports"].fillna(0)
    return out


def data_quality_table(df: pd.DataFrame) -> pd.DataFrame:
    fields = {
        "Payment amount": "payment_amount",
        "Injury severity": "outcome_label",
        "Patient age/sex/type": "has_patient_detail",
        "Event-to-report lag": "event_to_report_years",
        "State proxy": "state",
        "Secondary allegation": "alegatn2_label",
    }
    rows = []
    for label, column in fields.items():
        if column == "has_patient_detail":
            complete = df[column].mean()
        else:
            complete = df[column].notna().mean()
        rows.append({"field": label, "complete_pct": complete * 100})
    return pd.DataFrame(rows)
