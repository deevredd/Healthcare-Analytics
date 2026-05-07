import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from analyzer import (
    allegation_summary,
    data_quality_table,
    filtered_frame,
    kpis,
    payment_distribution,
    profession_summary,
    severity_mix,
    state_summary,
    yearly_trends,
)


DATA_PATH = Path("data/npdb_analytics.csv")
QUALITY_PATH = Path("data/data_quality.json")


st.set_page_config(page_title="ClaimLens NPDB", page_icon="CL", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    * { font-family: Inter, sans-serif; }
    header[data-testid="stHeader"],
    div[data-testid="stToolbar"],
    div[data-testid="stDecoration"],
    .stDeployButton {
        display: none !important;
    }
    .stApp { background: #090d14; color: #e5edf7; }
    .block-container {
        max-width: 1540px;
        padding-top: 1.35rem;
        padding-bottom: 2.5rem;
    }
    section[data-testid="stSidebar"] {
        background: #0d131f;
        border-right: 1px solid #1f2a3d;
    }
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span {
        color: #b8c4d6;
    }
    section[data-testid="stSidebar"] h3 {
        color: #f4f7fb;
        letter-spacing: 0;
    }
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: #7d8aa0;
    }
    div[data-baseweb="select"] > div {
        background: #111827;
        border-color: #273449;
    }
    div[data-baseweb="select"] *, div[data-baseweb="popover"] * {
        color: #e5edf7;
    }
    div[data-baseweb="popover"] ul {
        background: #111827;
        border: 1px solid #273449;
    }
    div[data-testid="stSlider"] label, div[data-testid="stMultiSelect"] label {
        color: #d5deea !important;
        font-weight: 700;
    }
    .badge {
        border: 1px solid #265b83;
        background: #0b2738;
        color: #7dd3fc;
        border-radius: 999px;
        padding: 7px 13px;
        font-size: 0.78rem;
        font-weight: 700;
        white-space: nowrap;
    }
    .topline {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        margin: 0 0 14px;
        padding: 0 0 14px;
        border-bottom: 1px solid #1f2a3d;
    }
    .topline h1 {
        color: #f6f9fc;
        font-size: 1.7rem;
        line-height: 1;
        margin: 0;
        letter-spacing: 0;
    }
    .topline p {
        color: #8ea0b8;
        font-size: 0.9rem;
        margin: 6px 0 0;
        line-height: 1.45;
    }
    .topline-meta {
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
        justify-content: flex-end;
    }
    .status-pill {
        border: 1px solid #254c3d;
        background: #09261f;
        color: #5eead4;
        border-radius: 999px;
        padding: 7px 12px;
        font-size: 0.78rem;
        font-weight: 800;
        white-space: nowrap;
    }
    .panel {
        background: #0f1724;
        border: 1px solid #1f2a3d;
        border-radius: 8px;
        padding: 16px 18px;
        box-shadow: 0 18px 45px rgba(0, 0, 0, 0.18);
    }
    .note {
        background: #121826;
        border: 1px solid #2a3a55;
        color: #a9b8cc;
        border-radius: 8px;
        padding: 11px 13px;
        font-size: 0.84rem;
        margin: 0 0 14px;
    }
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(5, minmax(0, 1fr));
        gap: 12px;
        margin: 0 0 14px;
    }
    .kpi-card {
        background: linear-gradient(180deg, #121b2a 0%, #0f1724 100%);
        border: 1px solid #26344c;
        border-radius: 8px;
        padding: 16px 16px;
        min-height: 104px;
        box-shadow: 0 12px 28px rgba(0, 0, 0, 0.2);
    }
    .kpi-label {
        color: #8ea0b8;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .04em;
    }
    .kpi-value {
        color: #f6f9fc;
        font-size: 1.75rem;
        font-weight: 800;
        line-height: 1;
        margin-top: 12px;
    }
    .kpi-sub {
        color: #7d8aa0;
        font-size: 0.78rem;
        margin-top: 8px;
    }
    .insight-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 12px;
        margin: 6px 0 18px;
    }
    .insight {
        background: #0f1724;
        border: 1px solid #223047;
        border-left: 4px solid #38bdf8;
        border-radius: 8px;
        padding: 13px 15px;
    }
    .insight b {
        display: block;
        color: #e5edf7;
        font-size: 0.94rem;
        margin-bottom: 4px;
    }
    .insight span {
        color: #93a4ba;
        font-size: 0.84rem;
        line-height: 1.45;
    }
    .chart-title {
        color: #f4f7fb;
        font-size: 1rem;
        font-weight: 800;
        margin: 4px 0 2px;
    }
    .chart-caption {
        color: #8493a8;
        font-size: 0.83rem;
        margin-bottom: 8px;
    }
    .section-label {
        color: #e5edf7;
        font-weight: 800;
        font-size: 0.92rem;
        margin: 12px 0 8px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        border-bottom: 1px solid #223047;
    }
    .stTabs [data-baseweb="tab"] {
        color: #8ea0b8 !important;
        background: transparent;
        border-radius: 8px 8px 0 0;
        padding: 10px 14px;
        font-weight: 700;
    }
    .stTabs [data-baseweb="tab"] p {
        color: #8ea0b8 !important;
        font-weight: 700;
    }
    .stTabs [aria-selected="true"] {
        background: #0f1724;
        border: 1px solid #26344c;
        border-bottom-color: #0f1724;
    }
    .stTabs [aria-selected="true"] p {
        color: #7dd3fc !important;
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid #26344c;
        border-radius: 8px;
    }
    div[data-testid="stMetric"] {
        background: #0f1724;
        border: 1px solid #26344c;
        border-radius: 8px;
        padding: 14px 16px;
    }
    div[data-testid="stMetric"] label { color: #8ea0b8; font-weight: 700; }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #f6f9fc; font-weight: 800; }
    .stMarkdown, .stMarkdown p, .stWrite, .stText {
        color: #a9b8cc;
    }
    .source {
        color: #74839a;
        font-size: 0.82rem;
        border-top: 1px solid #223047;
        padding-top: 16px;
        margin-top: 20px;
    }
    @media (max-width: 1000px) {
        .kpi-grid, .insight-grid { grid-template-columns: 1fr; }
        .topline { align-items: flex-start; flex-direction: column; }
        .topline-meta { justify-content: flex-start; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        st.error("Missing data/npdb_analytics.csv. Run `python3 pipeline.py` first.")
        st.stop()
    data = pd.read_csv(DATA_PATH)
    data["report_year"] = pd.to_numeric(data["report_year"], errors="coerce")
    return data


@st.cache_data
def load_quality() -> dict:
    if not QUALITY_PATH.exists():
        return {}
    return json.loads(QUALITY_PATH.read_text(encoding="utf-8"))


def money(value) -> str:
    if pd.isna(value):
        return "N/A"
    if abs(value) >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    if abs(value) >= 1_000:
        return f"${value / 1_000:.0f}k"
    return f"${value:,.0f}"


def number(value) -> str:
    if pd.isna(value):
        return "N/A"
    return f"{value:,.0f}"


AXIS_STYLE = dict(
    color="#8ea0b8",
    tickfont=dict(color="#8ea0b8", size=12),
    title_font=dict(color="#a9b8cc", size=12),
    gridcolor="#202b3d",
    zerolinecolor="#344258",
    linecolor="#344258",
)

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#0f1724",
    font=dict(color="#a9b8cc", family="Inter", size=12),
    margin=dict(l=10, r=10, t=12, b=12),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        font=dict(color="#a9b8cc"),
    ),
    hoverlabel=dict(bgcolor="#0b1020", bordercolor="#26344c", font=dict(color="#f6f9fc", family="Inter")),
)

CHART_CONFIG = {"displayModeBar": False, "responsive": True}


def polish_chart(fig):
    fig.update_layout(**PLOT_LAYOUT)
    fig.update_xaxes(**AXIS_STYLE)
    fig.update_yaxes(**AXIS_STYLE)
    fig.update_coloraxes(
        colorbar=dict(
            tickfont=dict(color="#8ea0b8"),
            title=dict(font=dict(color="#a9b8cc")),
        )
    )
    return fig


def chart_heading(title: str, caption: str):
    st.markdown(
        f"""
        <div class="chart-title">{title}</div>
        <div class="chart-caption">{caption}</div>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(label: str, value: str, sub: str):
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>
    """


df = load_data()
quality = load_quality()

min_year = int(df["report_year"].min())
max_year = int(df["report_year"].max())

with st.sidebar:
    st.markdown("### ClaimLens NPDB")
    st.caption("Malpractice payment intelligence from decoded NPDB public-use records.")
    year_range = st.slider("Report year", min_year, max_year, (max(min_year, 2004), max_year))
    groups = st.multiselect(
        "Practitioner group",
        sorted(df["profession_group"].dropna().unique()),
        default=[],
        placeholder="All groups",
    )
    states = st.multiselect(
        "State proxy",
        sorted(df["state"].dropna().unique()),
        default=[],
        placeholder="All states",
    )
    min_cases = st.slider("Minimum cases for rankings", 10, 250, 40, step=10)
    st.divider()
    st.caption("This app analyzes malpractice payment reports, not clinical quality or individual practitioners.")


filtered = filtered_frame(df, year_range, states, groups)
metrics = kpis(filtered)

st.markdown(
    f"""
    <div class="topline">
        <div>
            <h1>ClaimLens NPDB</h1>
            <p>Decoded malpractice payment intelligence across allegations, severity, geography, and practitioner fields.</p>
        </div>
        <div class="topline-meta">
            <span class="status-pill">{number(len(filtered))} reports in view</span>
            <span class="badge">NPDB public-use file</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="note">
    Payments are not proof of negligence. Values are nominal, and state is a reporting proxy derived from available NPDB location fields.
    </div>
    """,
    unsafe_allow_html=True,
)

lag_label = "Median event-to-report lag"
lag_value = f"{metrics['median_report_lag']:.1f} yrs" if pd.notna(metrics["median_report_lag"]) else "N/A"
top_allegation = allegation_summary(filtered, min_cases=min_cases).head(1)
top_label = top_allegation["alegatn1_label"].iloc[0] if len(top_allegation) else "N/A"
top_paid = money(top_allegation["total_paid"].iloc[0]) if len(top_allegation) else "N/A"

st.markdown(
    f"""
    <div class="kpi-grid">
        {kpi_card("Reports", number(metrics["reports"]), f"{year_range[0]}-{year_range[1]} filter window")}
        {kpi_card("Total paid", money(metrics["total_paid"]), "Nominal dollars, not adjusted")}
        {kpi_card("Median payment", money(metrics["median_payment"]), "Typical payment in filtered records")}
        {kpi_card("P90 payment", money(metrics["p90_payment"]), "Upper-tail payment threshold")}
        {kpi_card("Severe injury share", f"{metrics['severe_share']:.1f}%", "Outcome score of 6 or higher")}
    </div>
    <div class="insight-grid">
        <div class="insight"><b>Largest allegation pool</b><span>{top_label} accounts for {top_paid} in filtered payments.</span></div>
        <div class="insight"><b>{lag_label}</b><span>{lag_value} between malpractice event year and report year where both are valid.</span></div>
        <div class="insight"><b>Reliability first</b><span>Every chart is built from decoded NPDB fields and paired with completeness checks.</span></div>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_overview, tab_allegations, tab_geo, tab_reliability = st.tabs(
    ["Overview", "Allegation Intelligence", "Geography & Fields", "Reliability"]
)

with tab_overview:
    trend = yearly_trends(filtered)
    left, right = st.columns([1.25, 1])
    with left:
        chart_heading(
            "Report volume and median payment",
            "Bars show report volume; the line shows median payment for each report year.",
        )
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=trend["report_year"],
                y=trend["reports"],
                name="Reports",
                marker_color="#38bdf8",
                hovertemplate="%{x}: %{y:,} reports<extra></extra>",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=trend["report_year"],
                y=trend["median_payment"],
                name="Median payment",
                yaxis="y2",
                line=dict(color="#f97316", width=3),
                hovertemplate="%{x}: $%{y:,.0f}<extra></extra>",
            )
        )
        fig.update_layout(
            yaxis=dict(title="Reports"),
            yaxis2=dict(title="Median payment", overlaying="y", side="right", showgrid=False),
        )
        polish_chart(fig)
        fig.update_layout(yaxis2=dict(tickfont=dict(color="#8ea0b8"), title=dict(font=dict(color="#a9b8cc"))))
        st.plotly_chart(fig, config=CHART_CONFIG)
    with right:
        chart_heading(
            "Payment distribution",
            "Most reports are concentrated in sub-million payment bands.",
        )
        dist = payment_distribution(filtered)
        fig = px.bar(dist, x="payment_band", y="reports", color="reports")
        polish_chart(fig)
        fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Reports")
        fig.update_coloraxes(colorscale=[[0, "#1e3a5f"], [1, "#38bdf8"]], showscale=False)
        st.plotly_chart(fig, config=CHART_CONFIG)

    chart_heading(
        "Injury severity mix",
        "Report counts by NPDB outcome severity, colored by median payment amount.",
    )
    mix = severity_mix(filtered)
    mix["severity"] = mix["outcome_label"].fillna("Not reported")
    fig = px.bar(
        mix,
        x="severity",
        y="reports",
        color="median_payment",
        hover_data={"median_payment": ":$,.0f", "outcome_score": False},
    )
    polish_chart(fig)
    fig.update_layout(xaxis_title="", yaxis_title="Reports", showlegend=False)
    fig.update_xaxes(tickangle=-25)
    fig.update_coloraxes(colorscale=[[0, "#14332c"], [1, "#2dd4bf"]])
    st.plotly_chart(fig, config=CHART_CONFIG)

with tab_allegations:
    summary = allegation_summary(filtered, min_cases=min_cases)
    left, right = st.columns([1.15, 1])
    with left:
        chart_heading(
            "Highest total paid allegation codes",
            "Ranks allegations by aggregate payment, with color indicating severe injury share.",
        )
        top_paid = summary.head(15).copy()
        fig = px.bar(
            top_paid.sort_values("total_paid"),
            x="total_paid",
            y="alegatn1_label",
            orientation="h",
            color="severe_share",
            hover_data={"reports": ":,", "median_payment": ":$,.0f", "severe_share": ":.1f"},
        )
        polish_chart(fig)
        fig.update_layout(xaxis_title="Total paid", yaxis_title="")
        fig.update_coloraxes(colorscale=[[0, "#1e3a5f"], [1, "#fb7185"]], colorbar_title="Severe %")
        st.plotly_chart(fig, config=CHART_CONFIG)
    with right:
        chart_heading(
            "Frequency vs. median payment",
            "Bubble size represents total payment concentration for each allegation.",
        )
        fig = px.scatter(
            summary,
            x="reports",
            y="median_payment",
            size="total_paid",
            color="algnnatr_label",
            hover_name="alegatn1_label",
            hover_data={"total_paid": ":$,.0f", "severe_share": ":.1f"},
        )
        polish_chart(fig)
        fig.update_layout(xaxis_title="Reports", yaxis_title="Median payment")
        st.plotly_chart(fig, config=CHART_CONFIG)

    st.markdown('<div class="section-label">Ranked allegation table</div>', unsafe_allow_html=True)
    display = summary[
        ["algnnatr_label", "alegatn1_label", "reports", "total_paid", "median_payment", "severe_share", "median_report_lag"]
    ].rename(
        columns={
            "algnnatr_label": "Allegation group",
            "alegatn1_label": "Specific allegation",
            "reports": "Reports",
            "total_paid": "Total paid",
            "median_payment": "Median payment",
            "severe_share": "Severe injury %",
            "median_report_lag": "Median report lag",
        }
    )
    st.dataframe(
        display,
        width="stretch",
        hide_index=True,
        column_config={
            "Total paid": st.column_config.NumberColumn(format="$%d"),
            "Median payment": st.column_config.NumberColumn(format="$%d"),
            "Severe injury %": st.column_config.NumberColumn(format="%.1f%%"),
            "Median report lag": st.column_config.NumberColumn(format="%.1f years"),
        },
    )

with tab_geo:
    states_df = state_summary(filtered)
    chart_heading(
        "Total malpractice payments by state proxy",
        "State is derived from work state, then home state, then license state when available.",
    )
    fig = px.choropleth(
        states_df,
        locations="state",
        locationmode="USA-states",
        color="total_paid",
        scope="usa",
        hover_name="state",
        hover_data={"reports": ":,", "median_payment": ":$,.0f", "severe_share": ":.1f", "total_paid": ":$,.0f"},
    )
    polish_chart(fig)
    fig.update_layout(geo=dict(bgcolor="rgba(0,0,0,0)", lakecolor="#0f1724", landcolor="#111827"))
    fig.update_coloraxes(colorscale=[[0, "#13243b"], [1, "#38bdf8"]], colorbar_title="Total paid")
    st.plotly_chart(fig, config=CHART_CONFIG)

    chart_heading(
        "Practitioner fields with highest total payments",
        "Decoded license fields grouped into broad practitioner categories.",
    )
    prof = profession_summary(filtered).head(25)
    fig = px.bar(
        prof.sort_values("total_paid"),
        x="total_paid",
        y="licnfeld_label",
        color="profession_group",
        orientation="h",
        hover_data={"reports": ":,", "median_payment": ":$,.0f", "severe_share": ":.1f"},
    )
    polish_chart(fig)
    fig.update_layout(xaxis_title="Total paid", yaxis_title="")
    st.plotly_chart(fig, config=CHART_CONFIG)

with tab_reliability:
    q = data_quality_table(filtered)
    chart_heading(
        "Field completeness",
        "The dashboard shows data availability for every analytical field it relies on.",
    )
    fig = px.bar(
        q.sort_values("complete_pct"),
        x="complete_pct",
        y="field",
        orientation="h",
        text=q.sort_values("complete_pct")["complete_pct"].map(lambda x: f"{x:.1f}%"),
    )
    polish_chart(fig)
    fig.update_layout(xaxis_title="Complete records", yaxis_title="", showlegend=False)
    fig.update_xaxes(range=[0, 100])
    fig.update_traces(marker_color="#2dd4bf", textposition="outside", textfont=dict(color="#d5deea"))
    st.plotly_chart(fig, config=CHART_CONFIG)

    c1, c2, c3 = st.columns(3)
    c1.metric("Source rows", number(quality.get("source_rows", len(df))))
    c2.metric("Payment completeness", f"{quality.get('payment_complete_pct', 0):.1f}%")
    c3.metric("Severity completeness", f"{quality.get('severity_complete_pct', 0):.1f}%")

    st.markdown('<div class="section-label">Interpretation guardrails</div>', unsafe_allow_html=True)
    st.write(
        """
        The NPDB public-use file is intentionally de-identified. It is designed for statistical analysis, not for
        identifying clinicians, entities, or patients. The dashboard avoids unsupported diagnosis-delay claims and
        instead focuses on fields present in the file: malpractice allegation codes, payment amounts, injury severity,
        report year, event year, practitioner license field, and available state proxies.
        """
    )

st.markdown(
    """
    <div class="source">
    Source: National Practitioner Data Bank Public Use Data File and official Public Use Data File Format Specifications.
    Portfolio framing by ClaimLens NPDB. Not legal, medical, or actuarial advice.
    </div>
    """,
    unsafe_allow_html=True,
)
