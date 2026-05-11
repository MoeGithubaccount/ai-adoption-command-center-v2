"""Support Friction. Theme clusters only. Never message content."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from lib.loaders import load_tickets, MIN_COHORT_SIZE
from lib.theme import plotly_theme, ACCENT, NEUTRAL, WARN

st.set_page_config(page_title="Support Friction", layout="wide")
st.title("Support Friction")
st.caption("Themes in support tickets and consultations. "
           "Volume is hidden behind themes on purpose. Volume hides the actual friction.")

tickets = load_tickets()
ref_week = tickets.week.max()

# Window selector
window_label = st.radio("Rolling window", ["14 days", "30 days", "90 days"],
                       index=2, horizontal=True)
window_days = {"14 days": 14, "30 days": 30, "90 days": 90}[window_label]
window_start = ref_week - pd.Timedelta(days=window_days)
prior_start = window_start - pd.Timedelta(days=window_days)

recent = tickets[tickets.week >= window_start]
prior = tickets[(tickets.week >= prior_start) & (tickets.week < window_start)]

st.markdown(f"### Themes in the last {window_label}")

# Theme cluster bar with delta arrows
recent_themes = recent.theme.value_counts()
prior_themes = prior.theme.value_counts().reindex(recent_themes.index).fillna(0)
deltas = (recent_themes - prior_themes) / prior_themes.replace(0, 1)

theme_df = pd.DataFrame({
    "theme": recent_themes.index,
    "count": recent_themes.values,
    "delta": deltas.values,
}).sort_values("count", ascending=True)

fig = go.Figure()
fig.add_trace(go.Bar(
    x=theme_df["count"],
    y=theme_df.theme,
    orientation="h",
    marker_color=[WARN if d > 0.20 else ACCENT if d < -0.20 else NEUTRAL
                  for d in theme_df.delta],
    text=[f"{c:,}  ({d:+.0%})" for c, d in zip(theme_df["count"], theme_df.delta)],
    textposition="outside",
))
fig.update_xaxes(range=[0, theme_df["count"].max() * 1.3])
fig = plotly_theme(fig, height=400)
fig.update_layout(showlegend=False)
st.plotly_chart(fig, use_container_width=True)

st.caption("Amber: theme up >20% vs prior window. Teal: down >20%. Gray: stable.")

st.divider()

# Top rising themes
st.subheader("Top rising themes")
rising = theme_df[theme_df.delta > 0.10].sort_values("delta", ascending=False).head(3)
if rising.empty:
    st.info("No themes rising materially in this window.")
else:
    for _, row in rising.iterrows():
        with st.container(border=True):
            cols = st.columns([3, 1])
            cols[0].markdown(f"**{row.theme.replace('_', ' ').title()}**")
            cols[1].markdown(f"**{row.delta:+.0%}** vs prior")
            st.caption(f"Volume: {int(row['count']):,} tickets in the window.")

st.divider()

# Themes by department
st.subheader("Themes by department")
st.caption(f"Cohort minimum: {MIN_COHORT_SIZE} tickets. Smaller cohorts are suppressed.")

by_dept = recent.groupby(["department", "theme"]).size().unstack(fill_value=0)
by_dept = by_dept[by_dept.sum(axis=1) >= MIN_COHORT_SIZE]
by_dept_pct = by_dept.div(by_dept.sum(axis=1), axis=0)

fig = px.imshow(
    by_dept_pct.values,
    x=by_dept_pct.columns,
    y=by_dept_pct.index,
    color_continuous_scale=[[0, "#F8FAFC"], [1, ACCENT]],
    aspect="auto",
    text_auto=".0%",
)
fig.update_xaxes(side="top")
fig = plotly_theme(fig, height=380)
fig.update_layout(coloraxis_showscale=False, margin=dict(t=80))
st.plotly_chart(fig, use_container_width=True)

st.caption("Share of each department's tickets falling into each theme. "
           "Rows that read mostly one color indicate concentrated friction.")

st.divider()
st.subheader("What this view does not show")
st.markdown(
    "- No ticket content. Themes are derived from category tags applied at ticket creation.\n"
    "- No individual ticket detail. All cohorts are aggregated.\n"
    "- No support agent performance signals.\n"
    "- Themes are the question. Resolutions live in the ticketing system."
)
