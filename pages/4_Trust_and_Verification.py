"""Trust and Verification. Cohort-level confidence and verification signals."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from lib.loaders import load_surveys, MIN_COHORT_SIZE
from lib.theme import plotly_theme, ACCENT, WARN, NEUTRAL

st.set_page_config(page_title="Trust and Verification", layout="wide")
st.title("Trust and Verification")
st.caption("Are people using AI thoughtfully, not just frequently?")

surveys = load_surveys()

latest_month = surveys.month.max()
recent = surveys[surveys.month >= latest_month - pd.Timedelta(days=60)]

by_dept = recent.groupby("department").agg(
    n=("response_id", "count"),
    confidence_1=("confidence_workflow_1", "mean"),
    confidence_2=("confidence_workflow_2", "mean"),
    would_miss=("would_miss_it", "mean"),
    verify=("verify_outputs", "mean"),
).reset_index()

by_dept = by_dept[by_dept.n >= MIN_COHORT_SIZE]

st.subheader("Confidence and verification by function")
st.caption(f"Most recent 60 days of survey responses. Min cohort size: {MIN_COHORT_SIZE}.")

# Build a scatter: verify (x) vs confidence (y), size by n
fig = px.scatter(
    by_dept,
    x="verify",
    y="confidence_2",
    size="n",
    text="department",
    color="would_miss",
    color_continuous_scale=[[0, "#CBD5E1"], [1, ACCENT]],
    range_x=[1, 5],
    range_y=[1, 5],
)
fig.update_traces(textposition="top center")
fig.add_hline(y=3.0, line_dash="dot", line_color=NEUTRAL,
              annotation_text="Confidence threshold")
fig.add_vline(x=2.8, line_dash="dot", line_color=WARN,
              annotation_text="Verification threshold")
fig = plotly_theme(fig, height=500)
fig.update_layout(coloraxis_colorbar=dict(title="Would-miss-it"))
st.plotly_chart(fig, use_container_width=True)

st.caption("Departments below the verification threshold (left of dotted line) "
           "show risk of low-verification usage patterns. High usage + low verification "
           "is the failure mode this dashboard cares most about.")

st.divider()

st.subheader("Detail by function")
st.dataframe(
    by_dept.assign(
        confidence=(by_dept.confidence_1 + by_dept.confidence_2) / 2
    )[["department", "n", "confidence", "verify", "would_miss"]]
     .rename(columns={
        "n": "Responses",
        "confidence": "Avg confidence (1-5)",
        "verify": "Avg verify-outputs (1-5)",
        "would_miss": "Would-miss-it (1-5)",
     })
     .style.format({
        "Avg confidence (1-5)": "{:.2f}",
        "Avg verify-outputs (1-5)": "{:.2f}",
        "Would-miss-it (1-5)": "{:.2f}",
     }),
    hide_index=True,
    use_container_width=True,
)

st.caption("All scores are aggregated. No individual response is surfaced.")
