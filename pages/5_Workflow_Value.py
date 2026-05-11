"""Workflow Value. Stories and would-they-miss-it."""

import streamlit as st
import pandas as pd

from lib.loaders import load_stories, load_surveys, MIN_COHORT_SIZE
from lib.theme import ACCENT

st.set_page_config(page_title="Workflow Value", layout="wide")
st.title("Workflow Value")
st.caption("Evidence of changed work, not just activity.")

stories = load_stories()
surveys = load_surveys()

# Story count by dept
by_dept = stories.groupby("department").size().rename("stories").reset_index()

c1, c2 = st.columns(2)
with c1:
    st.subheader("Workflow change stories captured")
    st.bar_chart(by_dept.set_index("department")["stories"])

with c2:
    st.subheader("Would-they-miss-it (last 60 days)")
    latest = surveys.month.max()
    recent = surveys[surveys.month >= latest - pd.Timedelta(days=60)]
    wmi = recent.groupby("department").agg(
        n=("response_id", "count"),
        wmi=("would_miss_it", "mean"),
    )
    wmi = wmi[wmi.n >= MIN_COHORT_SIZE]
    st.bar_chart(wmi["wmi"])
    st.caption(f"Cohort minimum: {MIN_COHORT_SIZE}. Smaller cohorts suppressed.")

st.divider()

st.subheader("Recent stories")
st.caption("Voluntary, anonymized, tagged by function only.")

filter_dept = st.multiselect("Filter by function",
                              sorted(stories.department.unique()),
                              default=[])

filtered = stories.sort_values("week", ascending=False)
if filter_dept:
    filtered = filtered[filtered.department.isin(filter_dept)]

for _, s in filtered.head(15).iterrows():
    with st.container(border=True):
        cols = st.columns([2, 1])
        cols[0].markdown(f"**{s.department}**  ·  {s.workflow_tag}")
        cols[1].caption(f"{s.week.date()}")
        st.markdown(f'> {s.anonymized_excerpt}')

st.caption("Stories are submitted voluntarily through a quarterly story-capture sprint.")
