"""Training Impact. Stub - this page demonstrates the structure for the
training-to-usage lift analysis. Real implementation is a portfolio-extension
task; the page below is functional but minimal."""

import streamlit as st
import pandas as pd
import plotly.express as px

from lib.loaders import load_training, load_usage_weekly, load_employees, MIN_COHORT_SIZE
from lib.theme import plotly_theme, ACCENT, NEUTRAL

st.set_page_config(page_title="Training Impact", layout="wide")
st.title("Training Impact")
st.caption("Is training changing behavior? Attendance is easy. Lift is the question.")

events, attendance = load_training()
usage = load_usage_weekly()
employees = load_employees()

# Summary
total_events = len(events)
total_attendance = len(attendance)
attendees = attendance.employee_id.nunique()

c1, c2, c3 = st.columns(3)
c1.metric("Training events", f"{total_events}")
c2.metric("Attendance records", f"{total_attendance:,}")
c3.metric("Unique attendees", f"{attendees:,}")

st.divider()

# Attendance by type
st.subheader("Attendance by training type")
by_type = events.groupby("training_type").attended_count.sum().sort_values(ascending=True)
fig = px.bar(by_type, orientation="h", color_discrete_sequence=[ACCENT])
fig = plotly_theme(fig)
fig.update_layout(showlegend=False)
st.plotly_chart(fig, use_container_width=True)

st.divider()
st.info(
    "**Coming in v2.** Training-to-usage lift analysis. For each cohort that "
    "attended a training, compute weekly activity in the 30/60/90 days after, "
    "against a matched control cohort that did not attend. Report the lift as "
    "a confidence interval, not a single number."
)

st.markdown("""
Designed measurement:
- Build matched control cohort by department, role_band, tenure_band, and pre-training activity quartile.
- 4-week pre-training baseline.
- 12-week post-training tracking.
- Lift = post-rate(treatment) − post-rate(control), with bootstrap CI.
- Surface results only when both cohorts have ≥ 10 employees.
""")
