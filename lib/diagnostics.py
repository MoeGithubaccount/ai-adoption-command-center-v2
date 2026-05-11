"""
Adoption diagnosis library.

Each diagnosis is an INFERENCE drawn from a pattern of signals.
Every output here is labeled as inference in the UI.
"""

import pandas as pd
from .loaders import (
    load_employees, load_usage_weekly, load_tickets, load_surveys,
    load_manager_reinforcement, department_health, MIN_COHORT_SIZE
)

# Band ordering for manager reinforcement
BANDS = ["silent", "occasional", "supportive", "reinforcing", "modeling"]
BAND_RANK = {b: i for i, b in enumerate(BANDS)}


def manager_band_mode(reinforcement_df, dept, weeks_back=8):
    recent = reinforcement_df[
        (reinforcement_df.department == dept) &
        (reinforcement_df.week >= reinforcement_df.week.max() - pd.Timedelta(weeks=weeks_back))
    ]
    if len(recent) < MIN_COHORT_SIZE:
        return None
    return recent.reinforcement_band.mode().iloc[0]


def ticket_themes(tickets_df, dept, weeks_back=8):
    recent = tickets_df[
        (tickets_df.department == dept) &
        (tickets_df.week >= tickets_df.week.max() - pd.Timedelta(weeks=weeks_back))
    ]
    if len(recent) < 5:
        return {}
    return recent.theme.value_counts(normalize=True).to_dict()


def verify_score(surveys_df, dept):
    recent = surveys_df[surveys_df.department == dept].tail(60)
    if len(recent) < MIN_COHORT_SIZE:
        return None
    return float(recent.verify_outputs.mean())


def would_miss_score(surveys_df, dept):
    recent = surveys_df[surveys_df.department == dept].tail(60)
    if len(recent) < MIN_COHORT_SIZE:
        return None
    return float(recent.would_miss_it.mean())


def diagnose_department(dept):
    """Return list of (diagnosis, evidence_summary, confidence) for a department."""
    employees = load_employees()
    usage = load_usage_weekly()
    tickets = load_tickets()
    surveys = load_surveys()
    mgr = load_manager_reinforcement()

    health = department_health(usage, employees)
    row = health[health.department == dept]
    if row.empty:
        return []

    sustained_rate = float(row.sustained_rate.iloc[0])
    licensed = int(row.licensed.iloc[0])

    themes = ticket_themes(tickets, dept)
    band = manager_band_mode(mgr, dept)
    verify = verify_score(surveys, dept)
    would_miss = would_miss_score(surveys, dept)

    diagnoses = []

    # Reinforcement gap
    if band in ("silent", "occasional") and sustained_rate < 0.40:
        diagnoses.append({
            "name": "Reinforcement gap",
            "evidence": f"Manager band is '{band}'. Sustained active rate is {sustained_rate:.0%}.",
            "confidence": "high" if band == "silent" else "medium",
        })

    # Governance uncertainty
    if themes.get("governance_fear", 0) > 0.20:
        diagnoses.append({
            "name": "Governance uncertainty",
            "evidence": f"Governance-fear theme makes up {themes['governance_fear']:.0%} of recent tickets.",
            "confidence": "high" if themes.get("governance_fear", 0) > 0.35 else "medium",
        })

    # Tool confusion
    if themes.get("tool_selection", 0) > 0.18:
        diagnoses.append({
            "name": "Tool confusion",
            "evidence": f"Tool-selection theme is {themes['tool_selection']:.0%} of tickets.",
            "confidence": "medium",
        })

    # Verification/trust gap
    if verify is not None and verify < 2.8:
        diagnoses.append({
            "name": "Verification gap",
            "evidence": f"Self-reported verification score {verify:.1f}/5.0, below threshold of 2.8.",
            "confidence": "medium",
        })

    # Workflow mismatch (high usage, low would-miss)
    if sustained_rate > 0.45 and would_miss is not None and would_miss < 2.5:
        diagnoses.append({
            "name": "Workflow mismatch (low-stakes only)",
            "evidence": f"Sustained usage {sustained_rate:.0%} but 'would-miss-it' only {would_miss:.1f}/5.0.",
            "confidence": "medium",
        })

    # Spike and fade / curiosity-not-habit
    if sustained_rate < 0.35 and themes.get("workflow_question", 0) > 0.30:
        diagnoses.append({
            "name": "Curiosity-not-habit",
            "evidence": f"Low sustained rate {sustained_rate:.0%} with high workflow-question ticket share.",
            "confidence": "medium",
        })

    # Awareness/provisioning gap
    if licensed < 0.15 * employees[employees.department == dept].shape[0]:
        diagnoses.append({
            "name": "Awareness and provisioning gap",
            "evidence": "License coverage below 15% of department.",
            "confidence": "high",
        })

    if not diagnoses:
        diagnoses.append({
            "name": "No strong diagnostic signal",
            "evidence": "Patterns within normal range. Monitor.",
            "confidence": "low",
        })

    return diagnoses
