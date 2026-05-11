"""
Adoption Diagnosis. Per-function diagnosis detail with evidence.
"""

import streamlit as st
import pandas as pd

from lib.loaders import load_employees, load_usage_weekly, department_health
from lib.diagnostics import diagnose_department
from lib.interventions import intervention_for

st.set_page_config(page_title="Adoption Diagnosis", layout="wide")
st.title("Adoption Diagnosis")
st.caption("Why might adoption look the way it does in each function? "
           "Every diagnosis here is an inference, not a fact.")

employees = load_employees()
usage = load_usage_weekly()
health = department_health(usage, employees)

dept = st.selectbox("Select function",
                     sorted(health.department.unique()))

row = health[health.department == dept].iloc[0]

# Top metrics
c1, c2, c3 = st.columns(3)
c1.metric("Licensed", f"{int(row.licensed):,}")
c2.metric("Sustained active rate", f"{row.sustained_rate:.0%}")
c3.metric("Cohort status",
          "Investigate" if row.sustained_rate < 0.30
          else "Watch" if row.sustained_rate < 0.50
          else "Healthy")

st.divider()

diagnoses = diagnose_department(dept)
st.subheader(f"Likely diagnoses for {dept}")
st.caption("Listed in rough order of confidence. Multiple causes are common.")

for d in diagnoses:
    with st.container(border=True):
        cols = st.columns([3, 1])
        cols[0].markdown(f"### {d['name']}")
        cols[1].markdown(f"_confidence: {d['confidence']}_")
        st.caption(d["evidence"])

        intervention = intervention_for(d["name"])
        st.markdown(f"**Recommended intervention:** {intervention['intervention']}")
        st.caption(f"Owner: {intervention['owner']} · Follow-up: {intervention['follow_up_days']} days")
        if intervention["playbook"]:
            st.caption(f"Playbook: `{intervention['playbook']}`")

st.divider()

st.caption(
    "**Inferences on this page.** Diagnoses are derived from observed patterns "
    "in usage, support themes, survey signal, and manager reinforcement. They "
    "are working hypotheses for the enablement team, not statements of fact. "
    "Every diagnosis should be tested with a conversation in the function "
    "before an intervention is launched."
)
