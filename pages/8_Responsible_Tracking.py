"""
Responsible Tracking. This is a product page, not a footer.
Everything the dashboard does and does not do is named here.
"""

import streamlit as st

st.set_page_config(page_title="Responsible Tracking", layout="wide")
st.title("Responsible Tracking")
st.caption("The principles, the lines, and the tests this dashboard applies to itself.")

st.markdown("""
Adoption tracking has a failure mode. When the question becomes "who is not
using AI?" it stops being enablement and becomes surveillance. Cornell research
on algorithmic monitoring (Zitek et al., 2024) shows the same shift in
employees: more complaints, lower performance, higher intent to quit. The
unintended cost of measuring usage as compliance is the resistance it creates.

This dashboard is designed around one test for every signal: does this point
to a support action, or to an individual judgment? Signals that fail the
test are not surfaced.
""")

st.divider()

st.subheader("What this dashboard tracks")
st.markdown("""
- **Cohort-level usage trends.** Aggregated to department and role band only. Cohorts smaller than 10 are suppressed.
- **Theme patterns in support tickets.** Themes only. Never ticket content or individual ticket identity.
- **Training attendance at cohort level.** Plus cohort-level lift in subsequent usage.
- **Survey responses at cohort level.** Confidence, verification, would-they-miss-it.
- **Manager reinforcement, self-reported and opt-in.** Never inferred from message scanning.
- **Champion activity, opt-in.** Champions self-identify into the program.
- **Voluntary workflow change stories.** Anonymized, tagged by function only.
""")

st.subheader("What this dashboard never tracks")
st.markdown("""
- **Individual prompt content.** Not stored. Not analyzed. Not surfaced.
- **Per-user usage as a performance signal.** No part of this system feeds into reviews or rankings.
- **Identified user data in any aggregated view.** Cohort-only.
- **Sentiment derived from message or email content.**
- **Inferred manager reinforcement from communication patterns.** Self-report only.
- **"Power user" rankings.** Power users are not surfaced; the champion program is opt-in.
""")

st.subheader("What this dashboard tracks only with care")
st.markdown("""
- **Cohort segments smaller than 10.** Suppressed or merged into a larger cohort.
- **Department-level usage patterns.** Reported as bands and trends, not raw user counts that could narrow to individuals.
- **Verification behavior.** Aggregate survey data only. Individual verification patterns are never inferred.
""")

st.divider()

st.subheader("Operating principles")

st.markdown("""
1. **Groups, not people.** Every metric has a minimum cohort size of 10.
2. **Support, not score.** No metric in this system feeds performance evaluation.
3. **Themes, not content.** Support friction is clustered by theme, never by message text.
4. **Aggregated, not identified.** Stories are voluntary, anonymized, and tagged by function only.
5. **Diagnoses are inferences.** Every diagnosis is labeled as such, with the data behind it visible.
6. **Transparency by default.** Employees can see what the dashboard sees about their cohort.
7. **Action, not surveillance.** Every metric must map to a support action. Metrics that do not are removed.
""")

st.divider()

st.subheader("The test")
st.info(
    "Every signal in this dashboard is evaluated against one test: "
    "**does this point to a support action, or to an individual judgment?** "
    "If a signal cannot pass that test, it does not appear in this product."
)

st.divider()

st.subheader("Research basis")
st.markdown("""
- Zitek, E.M. & Schlund, R. (2024). *Algorithmic versus human surveillance leads to lower perceptions of autonomy and increased resistance.* Cornell University.
- Pew Research Center (2023). *Americans' Views on Use of AI to Monitor and Evaluate Workers.*
- Microsoft Work Trend Index 2025/2026.
- McKinsey, *The State of AI in 2025.*
- Deloitte, *State of Generative AI in the Enterprise* (2024–2025).
""")

st.caption("This is a portfolio prototype. Synthetic data. Fictional organization.")
