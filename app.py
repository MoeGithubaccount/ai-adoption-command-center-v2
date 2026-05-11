"""
AI Adoption Command Center
Entry page: Executive Snapshot.

This is a working demo built on synthetic data for a fictional organization.
Everything in this app is cohort-level only. No individual signals are surfaced.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from lib.loaders import (
    load_employees, load_usage_weekly, load_tickets,
    department_health, MIN_COHORT_SIZE
)
from lib.diagnostics import diagnose_department
from lib.theme import plotly_theme, ACCENT, NEUTRAL, WARN, STATE_COLORS

st.set_page_config(
    page_title="AI Adoption Command Center",
    page_icon="●",
    layout="wide",
)

# Sidebar
with st.sidebar:
    st.markdown("### Northstar Enterprise Services")
    st.caption("Fictional organization. Synthetic data.")
    st.divider()
    st.markdown("**Demo notes**")
    st.caption(f"Cohort minimum: {MIN_COHORT_SIZE}. Smaller cohorts are suppressed.")
    st.caption("Diagnoses are inferences, not facts.")
    st.divider()
    st.markdown("[Reference build doc on GitHub →](#)")

# Header
st.title("Executive Snapshot")
st.caption("Where adoption stands, what changed, what is on fire.")

# Load
employees = load_employees()
usage = load_usage_weekly()
tickets = load_tickets()

# Top-line metrics
licensed_count = int(employees.copilot_licensed.sum())
total = len(employees)
license_pct = licensed_count / total

ref_week = usage.week_start.max()
prior_ref = ref_week - pd.Timedelta(weeks=6)
recent_window = usage[usage.week_start >= prior_ref]
prior_window = usage[(usage.week_start >= prior_ref - pd.Timedelta(weeks=6)) &
                     (usage.week_start < prior_ref)]

active_recent = recent_window.groupby("employee_id").size()
active_prior = prior_window.groupby("employee_id").size()

sustained_recent = (active_recent >= 4).sum()
sustained_prior = (active_prior >= 4).sum()
sustained_rate = sustained_recent / licensed_count if licensed_count else 0
sustained_rate_prior = sustained_prior / licensed_count if licensed_count else 0
delta_pts = (sustained_rate - sustained_rate_prior) * 100

col1, col2, col3, col4 = st.columns(4)
col1.metric("Licensed employees", f"{licensed_count:,}", f"{license_pct:.0%} of org")
col2.metric("Sustained active rate", f"{sustained_rate:.0%}",
            f"{delta_pts:+.1f} pts vs prior 6 wks",
            delta_color="normal")
col3.metric("Recent tickets (4 wks)",
            f"{tickets[tickets.week >= ref_week - pd.Timedelta(weeks=4)].shape[0]:,}",
            help="Ticket volume only. Themes shown on Support Friction page.")
col4.metric("Stories captured (qtr)",
            f"{88}",
            help="Workflow change stories. Voluntary, anonymized.")

st.divider()

# Department health heatmap
st.subheader("Adoption health by department")
st.caption("Sustained active rate over the past 6 weeks. Cohorts under "
           f"{MIN_COHORT_SIZE} are suppressed.")

health = department_health(usage, employees, ref_week=ref_week)
health = health.sort_values("sustained_rate", ascending=True)

# Heatmap as horizontal bar
fig = go.Figure(go.Bar(
    x=health.sustained_rate,
    y=health.department,
    orientation="h",
    marker=dict(
        color=[STATE_COLORS["intervene"] if r < 0.30
               else STATE_COLORS["watch"] if r < 0.50
               else STATE_COLORS["healthy"]
               for r in health.sustained_rate],
    ),
    text=[f"{r:.0%}" for r in health.sustained_rate],
    textposition="outside",
    hovertemplate="<b>%{y}</b><br>Sustained active: %{x:.1%}<br>" +
                  "Licensed: %{customdata}<extra></extra>",
    customdata=health.licensed,
))
fig.update_xaxes(tickformat=".0%", range=[0, max(health.sustained_rate.max() * 1.2, 0.6)])
fig.update_yaxes(categoryorder="array", categoryarray=health.department.tolist())
fig = plotly_theme(fig, height=380)
fig.update_layout(showlegend=False)
st.plotly_chart(fig, use_container_width=True)

st.caption("Color: green ≥50%, amber 30–50%, red <30%. These thresholds are "
           "configurable per organization. They are not normative.")

st.divider()

# Top intervention queue items preview
st.subheader("Top intervention queue items")
st.caption("Diagnoses are inferences. Full detail on the Intervention Queue page.")

# Find functions with low sustained rate and surface their top diagnosis
weak_depts = health[health.sustained_rate < 0.40].sort_values("sustained_rate").head(3)

if len(weak_depts) == 0:
    st.info("No P1 items in queue. Monitor and revisit weekly.")
else:
    for _, row in weak_depts.iterrows():
        dept = row.department
        diagnoses = diagnose_department(dept)
        top = diagnoses[0]
        with st.container(border=True):
            cols = st.columns([3, 1])
            cols[0].markdown(f"**{dept}** — sustained active {row.sustained_rate:.0%}")
            cols[1].markdown(f":red[**P1**]" if row.sustained_rate < 0.30
                             else ":orange[**P2**]")
            st.markdown(f"*Likely diagnosis (inference):* **{top['name']}**")
            st.caption(top["evidence"])

st.divider()

# Recent change stories
st.subheader("Recent workflow change stories")
st.caption("Voluntary, anonymized excerpts. Tagged by function only.")

from lib.loaders import load_stories
stories = load_stories().sort_values("week", ascending=False).head(5)
for _, s in stories.iterrows():
    with st.container(border=True):
        st.markdown(f"**{s.department}** · {s.workflow_tag} · {s.week.date()}")
        st.caption(f'"{s.anonymized_excerpt}"')

st.divider()
st.caption("**This is synthetic data on a fictional organization.** "
           "Built as a portfolio demonstration of how an enablement decision "
           "system could work. The patterns are modeled on public research, "
           "not on any real organization.")
