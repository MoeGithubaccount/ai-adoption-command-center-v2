"""
Intervention Queue. The centerpiece.

For each department showing weak adoption, surface the top diagnosis, the
recommended intervention, owner, priority, playbook, follow-up window, and
the success signal to watch.
"""

import streamlit as st
import pandas as pd

from lib.loaders import (
    load_employees, load_usage_weekly, department_health
)
from lib.diagnostics import diagnose_department
from lib.interventions import intervention_for
from lib.theme import STATE_COLORS

st.set_page_config(page_title="Intervention Queue", layout="wide")

st.title("Intervention Queue")
st.caption("What the enablement team should do this week, and why. "
           "Every item has an owner, a playbook, a follow-up window, and a defined success signal.")

employees = load_employees()
usage = load_usage_weekly()
health = department_health(usage, employees)

# Build the queue
queue = []
for _, row in health.iterrows():
    dept = row.department
    sustained = float(row.sustained_rate)
    diagnoses = diagnose_department(dept)

    if diagnoses[0]["name"] == "No strong diagnostic signal":
        continue

    # Priority by sustained rate
    if sustained < 0.30:
        priority = "P1"
    elif sustained < 0.45:
        priority = "P2"
    else:
        priority = "P3"

    top = diagnoses[0]
    intervention = intervention_for(top["name"])

    queue.append({
        "dept": dept,
        "sustained": sustained,
        "priority": priority,
        "diagnosis": top["name"],
        "evidence": top["evidence"],
        "confidence": top["confidence"],
        "intervention": intervention["intervention"],
        "owner": intervention["owner"],
        "playbook": intervention["playbook"],
        "follow_up_days": intervention["follow_up_days"],
        "success_signal": intervention["success_signal"],
        "all_diagnoses": diagnoses,
    })

# Sort by priority then sustained rate ascending
priority_order = {"P1": 0, "P2": 1, "P3": 2}
queue.sort(key=lambda x: (priority_order[x["priority"]], x["sustained"]))

# Filter
priority_filter = st.multiselect("Priority filter", ["P1", "P2", "P3"], default=["P1", "P2", "P3"])

st.divider()

# Render items
shown = [q for q in queue if q["priority"] in priority_filter]
st.markdown(f"### {len(shown)} items in queue")

for q in shown:
    color = "#9F1239" if q["priority"] == "P1" else "#B45309" if q["priority"] == "P2" else "#64748B"
    with st.container(border=True):
        # Header
        cols = st.columns([4, 1])
        cols[0].markdown(f"### {q['dept']}")
        cols[1].markdown(f"<div style='text-align:right; color:{color}; font-weight:600; font-size:1.1rem'>{q['priority']}</div>",
                         unsafe_allow_html=True)

        # Pattern
        st.markdown("**Pattern detected**")
        st.caption(f"Sustained active rate {q['sustained']:.0%} over the past 6 weeks.")

        # Diagnosis
        st.markdown(f"**Likely diagnosis** _(inference, confidence: {q['confidence']})_")
        st.markdown(f"› {q['diagnosis']}")
        st.caption(q["evidence"])

        # Alternative diagnoses
        if len(q["all_diagnoses"]) > 1:
            with st.expander(f"Other possible diagnoses ({len(q['all_diagnoses']) - 1})"):
                for d in q["all_diagnoses"][1:]:
                    st.markdown(f"- **{d['name']}** ({d['confidence']} confidence) — {d['evidence']}")

        # Intervention
        st.markdown("**Recommended intervention**")
        st.markdown(f"› {q['intervention']}")

        # Detail row
        cols = st.columns(3)
        cols[0].markdown(f"**Owner**")
        cols[0].caption(q["owner"])
        cols[1].markdown(f"**Follow-up**")
        cols[1].caption(f"{q['follow_up_days']} days")
        cols[2].markdown(f"**Playbook**")
        cols[2].caption(q["playbook"] or "—")

        # Success signal
        st.markdown("**Success signal to watch**")
        st.caption(q["success_signal"])

st.divider()
st.caption(
    "**A note on confidence.** Each diagnosis is an inference drawn from a "
    "pattern of signals. Confidence labels reflect how clean the pattern is. "
    "Alternate diagnoses are listed because real adoption problems usually "
    "have more than one cause."
)
