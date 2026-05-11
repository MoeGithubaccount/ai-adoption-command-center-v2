"""Adoption Health by function."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from lib.loaders import (
    load_employees, load_usage_weekly, load_manager_reinforcement,
    department_health, MIN_COHORT_SIZE
)
from lib.theme import plotly_theme, ACCENT, NEUTRAL, BAND_COLORS, STATE_COLORS

st.set_page_config(page_title="Adoption Health", layout="wide")

st.title("Adoption Health")
st.caption("Where adoption is working and where it is stalling. Department-level only.")

employees = load_employees()
usage = load_usage_weekly()
mgr = load_manager_reinforcement()

ref_week = usage.week_start.max()
health = department_health(usage, employees, ref_week=ref_week)

# Manager band per dept (most recent 8 weeks)
recent_mgr = mgr[mgr.week >= ref_week - pd.Timedelta(weeks=8)]
band_counts = recent_mgr.groupby(["department", "reinforcement_band"]).size().unstack(fill_value=0)
bands = ["silent", "occasional", "supportive", "reinforcing", "modeling"]
band_pct = band_counts.reindex(columns=bands, fill_value=0)
band_pct = band_pct.div(band_pct.sum(axis=1), axis=0)

# Frequency / consistency per dept
recent_usage = usage[usage.week_start >= ref_week - pd.Timedelta(weeks=6)]
freq = recent_usage.groupby("department").weekly_actions.mean().rename("avg_weekly_actions")
surfaces = recent_usage.groupby("department").distinct_surfaces.mean().rename("avg_surfaces")

merged = health.set_index("department")
merged = merged.join(freq).join(surfaces).reset_index()

st.subheader("Function-level adoption signals")
st.caption("All cohorts shown have at least 10 licensed employees.")

# Multi-column table-ish view
for _, row in merged.sort_values("sustained_rate", ascending=False).iterrows():
    state = ("healthy" if row.sustained_rate >= 0.50
             else "watch" if row.sustained_rate >= 0.30
             else "intervene")
    color = STATE_COLORS[state]

    with st.container(border=True):
        cols = st.columns([2, 1, 1, 1, 1])
        cols[0].markdown(f"### {row.department}")
        cols[0].caption(f"{int(row.licensed):,} licensed")
        cols[1].metric("Sustained active", f"{row.sustained_rate:.0%}")
        cols[2].metric("Avg actions/week", f"{row.avg_weekly_actions:.1f}")
        cols[3].metric("Surface diversity", f"{row.avg_surfaces:.1f}")
        cols[4].markdown(f"<div style='text-align:center;color:{color};font-weight:600;margin-top:1.5rem'>{state.upper()}</div>",
                         unsafe_allow_html=True)

        # Manager band
        if row.department in band_pct.index:
            mb = band_pct.loc[row.department]
            dominant = mb.idxmax()
            st.caption(f"Manager reinforcement band (most common, last 8 wks): **{dominant}**")

st.divider()

st.subheader("Manager reinforcement distribution")
st.caption("Self-reported, opt-in. Most recent 8 weeks. Cohort-suppressed.")

fig = go.Figure()
for band in bands:
    if band in band_pct.columns:
        fig.add_trace(go.Bar(
            name=band,
            y=band_pct.index,
            x=band_pct[band],
            orientation="h",
            marker_color=BAND_COLORS[band],
        ))
fig.update_layout(barmode="stack")
fig.update_xaxes(tickformat=".0%", range=[0, 1])
fig = plotly_theme(fig, height=400)
st.plotly_chart(fig, use_container_width=True)

st.caption(
    "Silent and occasional bands above ~50% in a function correlate strongly with "
    "weak sustained active rates. This is not a causal claim — it is a pattern "
    "worth investigating per function on the Diagnosis page."
)
