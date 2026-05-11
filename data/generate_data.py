"""
Northstar Enterprise Services - synthetic data generator.

Fictional 4,200-person organization with 10 departments.
12 months of weekly usage, training, support tickets, surveys, manager reinforcement,
champion activity, and workflow stories.

Patterns are encoded per the build doc. Noise is intentional.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

RNG = np.random.default_rng(42)
OUT = Path(__file__).parent

# ------------------------------------------------------------
# Org structure
# ------------------------------------------------------------

DEPARTMENTS = {
    "Marketing":         {"size": 320, "licensed_pct": 0.85},
    "IT":                {"size": 480, "licensed_pct": 0.90},
    "Finance":           {"size": 380, "licensed_pct": 0.75},
    "Human Resources":   {"size": 220, "licensed_pct": 0.80},
    "Operations":        {"size": 920, "licensed_pct": 0.40},
    "Research":          {"size": 410, "licensed_pct": 0.78},
    "Legal":             {"size": 110, "licensed_pct": 0.65},
    "Executive Office":  {"size":  60, "licensed_pct": 0.95},
    "Customer Support":  {"size": 780, "licensed_pct": 0.55},
    "Facilities":        {"size": 520, "licensed_pct": 0.08},
}

# Per-department behavior profile.
# Higher base_activity = more weekly actions per active user.
# stickiness = probability of being active again next week given active this week.
# spike_only = chance an "active" user is one-week-only.
# verify_baseline = mean self-reported verification rate (1-5).
# would_miss_baseline = mean "would-they-miss-it" score (1-5).
# manager_band_weights = probabilities over [silent, occasional, supportive, reinforcing, modeling].
PROFILES = {
    "Marketing":        dict(base_activity=22, stickiness=0.78, spike_only=0.10, verify=3.7, would_miss=3.9,
                             manager_weights=[0.05, 0.10, 0.30, 0.30, 0.25]),
    "IT":               dict(base_activity=28, stickiness=0.74, spike_only=0.12, verify=3.4, would_miss=2.7,  # contradiction
                             manager_weights=[0.10, 0.25, 0.35, 0.20, 0.10]),
    "Finance":          dict(base_activity=10, stickiness=0.42, spike_only=0.30, verify=3.5, would_miss=2.4,
                             manager_weights=[0.20, 0.45, 0.25, 0.08, 0.02]),
    "Human Resources":  dict(base_activity=12, stickiness=0.48, spike_only=0.22, verify=3.2, would_miss=2.6,
                             manager_weights=[0.15, 0.40, 0.30, 0.10, 0.05]),
    "Operations":       dict(base_activity=8,  stickiness=0.38, spike_only=0.35, verify=3.0, would_miss=2.1,
                             manager_weights=[0.55, 0.30, 0.10, 0.04, 0.01]),
    "Research":         dict(base_activity=35, stickiness=0.72, spike_only=0.10, verify=2.4, would_miss=3.6,  # low verify
                             manager_weights=[0.15, 0.30, 0.30, 0.15, 0.10]),
    "Legal":            dict(base_activity=6,  stickiness=0.30, spike_only=0.45, verify=3.6, would_miss=1.9,
                             manager_weights=[0.65, 0.25, 0.08, 0.02, 0.00]),
    "Executive Office": dict(base_activity=18, stickiness=0.45, spike_only=0.30, verify=3.3, would_miss=2.8,
                             manager_weights=[0.20, 0.30, 0.25, 0.15, 0.10]),
    "Customer Support": dict(base_activity=11, stickiness=0.50, spike_only=0.25, verify=3.4, would_miss=2.7,
                             manager_weights=[0.30, 0.40, 0.20, 0.07, 0.03]),
    "Facilities":       dict(base_activity=4,  stickiness=0.25, spike_only=0.50, verify=3.0, would_miss=1.6,
                             manager_weights=[0.75, 0.20, 0.04, 0.01, 0.00]),
}

# Customer Support gets an intervention bump in month 5 (week 20).
INTERVENTION_WEEK = 20
INTERVENTION_DEPT = "Customer Support"

# Ticket theme weights per department.
TICKET_THEMES = ["tool_selection", "governance_fear", "prompt_skill",
                 "verification", "workflow_question", "access_issue", "other"]

THEME_WEIGHTS = {
    "Marketing":        [0.10, 0.05, 0.15, 0.10, 0.40, 0.10, 0.10],
    "IT":               [0.20, 0.05, 0.10, 0.10, 0.20, 0.20, 0.15],
    "Finance":          [0.20, 0.40, 0.10, 0.10, 0.10, 0.05, 0.05],
    "Human Resources":  [0.10, 0.15, 0.30, 0.15, 0.20, 0.05, 0.05],
    "Operations":       [0.10, 0.10, 0.20, 0.05, 0.40, 0.10, 0.05],
    "Research":         [0.05, 0.10, 0.10, 0.35, 0.25, 0.10, 0.05],
    "Legal":            [0.25, 0.45, 0.05, 0.05, 0.10, 0.05, 0.05],
    "Executive Office": [0.25, 0.10, 0.20, 0.10, 0.25, 0.05, 0.05],
    "Customer Support": [0.10, 0.05, 0.20, 0.10, 0.35, 0.15, 0.05],
    "Facilities":       [0.10, 0.05, 0.15, 0.05, 0.30, 0.30, 0.05],
}


# ------------------------------------------------------------
# Build employees
# ------------------------------------------------------------

def build_employees():
    rows = []
    eid = 1000
    for dept, info in DEPARTMENTS.items():
        for _ in range(info["size"]):
            role = RNG.choice(["IC", "Manager", "Director"], p=[0.82, 0.15, 0.03])
            tenure = RNG.choice(["<1yr", "1-3yr", "3-7yr", "7+yr"], p=[0.20, 0.35, 0.30, 0.15])
            licensed = RNG.random() < info["licensed_pct"]
            # Stagger license assignment dates across the year
            assign_date = pd.Timestamp("2025-05-01") + pd.Timedelta(days=int(RNG.integers(0, 300)))
            rows.append({
                "employee_id": f"E{eid:05d}",
                "department": dept,
                "role_band": role,
                "tenure_band": tenure,
                "copilot_licensed": licensed,
                "license_assigned_date": assign_date if licensed else pd.NaT,
            })
            eid += 1
    return pd.DataFrame(rows)


# ------------------------------------------------------------
# Build weekly usage
# ------------------------------------------------------------

def build_usage_weekly(employees):
    # 52 weeks ending ~May 3, 2026
    weeks = pd.date_range(end="2026-05-03", periods=52, freq="W-MON")
    rows = []

    licensed = employees[employees.copilot_licensed].copy()
    licensed["activity_state"] = "dormant"  # track simple state per employee

    for w_i, week in enumerate(weeks):
        for dept, profile in PROFILES.items():
            dept_emps = licensed[licensed.department == dept]
            if len(dept_emps) == 0:
                continue

            # Has license been assigned by this week?
            active_eligible = dept_emps[dept_emps.license_assigned_date <= week]
            if len(active_eligible) == 0:
                continue

            stickiness = profile["stickiness"]
            spike_only = profile["spike_only"]
            base = profile["base_activity"]

            # Apply Customer Support intervention bump from week 20
            if dept == INTERVENTION_DEPT and w_i >= INTERVENTION_WEEK:
                stickiness = min(0.85, stickiness + 0.25)
                base = base + 8
                spike_only = max(0.05, spike_only - 0.15)

            # Holiday dip mid-December
            holiday_dip = 0.6 if 31 <= w_i <= 33 else 1.0

            for _, emp in active_eligible.iterrows():
                # Probability of activity this week scales with dept stickiness.
                # High stickiness depts have habit-formers; low stickiness depts
                # have more spike-then-fade patterns.
                p_active = stickiness * 0.85  # base activity probability per week
                # Spike-only employees only fire occasionally
                if RNG.random() < spike_only:
                    p_active *= 0.3
                p_active *= holiday_dip
                is_active = RNG.random() < p_active

                if is_active:
                    actions = max(1, int(RNG.normal(base, base * 0.4)))
                    surfaces = int(np.clip(RNG.normal(2.5, 1.2), 1, 5))
                    sustained = RNG.random() < stickiness
                    rows.append({
                        "employee_id": emp.employee_id,
                        "department": dept,
                        "week_start": week,
                        "weekly_actions": actions,
                        "distinct_surfaces": surfaces,
                        "sustained_flag": sustained,
                    })

    return pd.DataFrame(rows)


# ------------------------------------------------------------
# Build training data
# ------------------------------------------------------------

def build_training(employees):
    events = []
    attendance = []

    training_types = ["Foundations", "Workflow Lab", "Verification", "Office Hours"]
    weeks = pd.date_range(start="2025-09-01", end="2026-05-01", freq="2W")

    tid = 1
    for week in weeks:
        for _ in range(int(RNG.integers(1, 4))):
            ttype = RNG.choice(training_types)
            dept = RNG.choice(list(DEPARTMENTS.keys()))
            attended_target = int(RNG.integers(8, 40))
            events.append({
                "training_id": f"T{tid:04d}",
                "training_type": ttype,
                "date": week,
                "department_invited": dept,
                "attended_count": attended_target,
            })

            dept_emps = employees[(employees.department == dept) & employees.copilot_licensed]
            if len(dept_emps) > 0:
                attendees = dept_emps.sample(
                    min(attended_target, len(dept_emps)), random_state=int(week.timestamp()) % 2**32
                )
                for _, emp in attendees.iterrows():
                    attendance.append({
                        "employee_id": emp.employee_id,
                        "training_id": f"T{tid:04d}",
                        "attended": True,
                    })
            tid += 1

    return pd.DataFrame(events), pd.DataFrame(attendance)


# ------------------------------------------------------------
# Build support tickets
# ------------------------------------------------------------

def build_support_tickets():
    weeks = pd.date_range(end="2026-05-03", periods=52, freq="W-MON")
    rows = []
    tid = 1
    for w_i, week in enumerate(weeks):
        for dept, info in DEPARTMENTS.items():
            # Volume scales with size and adoption
            base_rate = info["size"] * info["licensed_pct"] * 0.012
            # Rising governance fear in Finance, rising verification in Research
            seasonal = 1.0
            if dept == "Finance" and w_i > 30:
                seasonal = 1.5
            if dept == "Research" and w_i > 25:
                seasonal = 1.4
            n_tickets = max(0, int(RNG.poisson(base_rate * seasonal)))

            weights = THEME_WEIGHTS[dept].copy()
            # Seasonal shifts
            if dept == "Finance" and w_i > 30:
                weights[1] = weights[1] * 1.6  # governance_fear
                weights = list(np.array(weights) / sum(weights))
            if dept == "Research" and w_i > 25:
                weights[3] = weights[3] * 1.5  # verification
                weights = list(np.array(weights) / sum(weights))
            if dept == INTERVENTION_DEPT and w_i >= INTERVENTION_WEEK:
                weights[4] = weights[4] * 0.6  # workflow_question drops
                weights = list(np.array(weights) / sum(weights))

            for _ in range(n_tickets):
                theme = RNG.choice(TICKET_THEMES, p=weights)
                rows.append({
                    "ticket_id": f"S{tid:06d}",
                    "week": week,
                    "department": dept,
                    "theme": theme,
                    "resolved_days": int(RNG.integers(1, 6)),
                })
                tid += 1

    return pd.DataFrame(rows)


# ------------------------------------------------------------
# Build survey responses
# ------------------------------------------------------------

def build_surveys():
    months = pd.date_range(start="2025-08-01", end="2026-05-01", freq="MS")
    rows = []
    rid = 1
    for month in months:
        for dept, profile in PROFILES.items():
            # ~15-30 responses per dept per month
            n = int(RNG.integers(15, 35))
            for _ in range(n):
                conf1 = float(np.clip(RNG.normal(profile["verify"] - 0.2, 0.7), 1, 5))
                conf2 = float(np.clip(RNG.normal(profile["verify"], 0.7), 1, 5))
                miss = float(np.clip(RNG.normal(profile["would_miss"], 0.8), 1, 5))
                verify = float(np.clip(RNG.normal(profile["verify"], 0.6), 1, 5))
                rows.append({
                    "response_id": f"R{rid:06d}",
                    "month": month,
                    "department": dept,
                    "confidence_workflow_1": round(conf1, 2),
                    "confidence_workflow_2": round(conf2, 2),
                    "would_miss_it": round(miss, 2),
                    "verify_outputs": round(verify, 2),
                })
                rid += 1
    return pd.DataFrame(rows)


# ------------------------------------------------------------
# Build manager reinforcement
# ------------------------------------------------------------

def build_manager_reinforcement(employees):
    weeks = pd.date_range(end="2026-05-03", periods=52, freq="W-MON")
    bands = ["silent", "occasional", "supportive", "reinforcing", "modeling"]

    managers = employees[employees.role_band.isin(["Manager", "Director"])].copy()
    rows = []

    for _, mgr in managers.iterrows():
        profile = PROFILES[mgr.department]
        for w_i, week in enumerate(weeks):
            weights = profile["manager_weights"]
            # Customer Support intervention shifts the distribution
            if mgr.department == INTERVENTION_DEPT and w_i >= INTERVENTION_WEEK:
                weights = [0.10, 0.25, 0.35, 0.20, 0.10]
            # Only ~60% of managers self-report each week
            if RNG.random() < 0.6:
                band = RNG.choice(bands, p=weights)
                rows.append({
                    "manager_id": mgr.employee_id,
                    "department": mgr.department,
                    "week": week,
                    "reinforcement_band": band,
                })

    return pd.DataFrame(rows)


# ------------------------------------------------------------
# Build champion activity
# ------------------------------------------------------------

def build_champion_activity():
    # Champion counts per department (small, opt-in)
    champ_counts = {
        "Marketing": 6, "IT": 5, "Research": 4, "Customer Support": 3,
        "Executive Office": 2, "Human Resources": 2, "Finance": 1,
        "Operations": 1, "Legal": 0, "Facilities": 0,
    }
    weeks = pd.date_range(end="2026-05-03", periods=52, freq="W-MON")
    activity_types = ["demo", "peer_coach", "example_share", "content"]
    rows = []
    cid = 1
    for dept, count in champ_counts.items():
        for c_i in range(count):
            champ_id = f"C{cid:04d}"
            # Activity baseline varies by department engagement
            base = 3 if dept in ("Marketing", "IT", "Customer Support") else 1.5
            for week in weeks:
                # Each champion does some activity ~70% of weeks
                if RNG.random() < 0.7:
                    activity = RNG.choice(activity_types)
                    n = max(0, int(RNG.poisson(base)))
                    if n > 0:
                        rows.append({
                            "champion_id": champ_id,
                            "department": dept,
                            "week": week,
                            "activity_type": activity,
                            "count": n,
                        })
            cid += 1
    return pd.DataFrame(rows)


# ------------------------------------------------------------
# Build workflow stories
# ------------------------------------------------------------

def build_workflow_stories():
    # Stories per dept reflect the patterns
    story_volume = {
        "Marketing": 22, "IT": 14, "Customer Support": 18,  # CS jumps after intervention
        "Research": 12, "Executive Office": 6, "Human Resources": 4,
        "Finance": 5, "Operations": 6, "Legal": 1, "Facilities": 0,
    }
    workflows = {
        "Marketing": ["campaign_brief", "audience_research", "content_drafting"],
        "IT": ["script_drafting", "doc_search", "ticket_triage"],
        "Customer Support": ["case_triage", "knowledge_lookup", "response_drafting"],
        "Research": ["literature_review", "synthesis", "writing"],
        "Executive Office": ["briefing_prep", "summarization"],
        "Human Resources": ["policy_drafting", "interview_questions"],
        "Finance": ["analysis_prep", "model_review"],
        "Operations": ["sop_drafting", "data_summary"],
        "Legal": ["clause_review"],
        "Facilities": [],
    }
    excerpts = [
        "Used Copilot to triage the first pass of cases — cut my morning by an hour.",
        "Drafted the campaign brief from notes in five minutes; would have taken thirty.",
        "Asked Copilot to summarize the meeting; corrected two facts but the structure saved time.",
        "Did the first pass of the policy update in Copilot; spent more time editing than writing.",
        "Pulled together a customer history summary in seconds. Verified every fact before sending.",
        "Wrote a draft response in Copilot, rewrote about half of it, still net positive.",
        "Generated three alternate analyses to compare. Useful for stress-testing.",
        "Asked Copilot to find a quote from a past report. Found it. Verified location.",
    ]
    rows = []
    sid = 1
    weeks = pd.date_range(end="2026-05-03", periods=52, freq="W-MON")
    for dept, count in story_volume.items():
        wfs = workflows[dept]
        if not wfs or count == 0:
            continue
        for _ in range(count):
            # Customer Support stories cluster after week 20
            if dept == INTERVENTION_DEPT:
                week = RNG.choice(weeks[INTERVENTION_WEEK:])
            else:
                week = RNG.choice(weeks)
            rows.append({
                "story_id": f"W{sid:04d}",
                "week": week,
                "department": dept,
                "workflow_tag": RNG.choice(wfs),
                "length_sentences": int(RNG.integers(2, 5)),
                "anonymized_excerpt": RNG.choice(excerpts),
            })
            sid += 1
    return pd.DataFrame(rows)


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():
    print("Building employees...")
    emp = build_employees()
    emp.to_csv(OUT / "employees.csv", index=False)
    print(f"  {len(emp):,} employees")

    print("Building usage_weekly...")
    usage = build_usage_weekly(emp)
    usage.to_csv(OUT / "usage_weekly.csv", index=False)
    print(f"  {len(usage):,} user-week records")

    print("Building training...")
    events, attendance = build_training(emp)
    events.to_csv(OUT / "training_events.csv", index=False)
    attendance.to_csv(OUT / "training_attendance.csv", index=False)
    print(f"  {len(events)} training events, {len(attendance)} attendance records")

    print("Building support_tickets...")
    tickets = build_support_tickets()
    tickets.to_csv(OUT / "support_tickets.csv", index=False)
    print(f"  {len(tickets):,} tickets")

    print("Building surveys...")
    surveys = build_surveys()
    surveys.to_csv(OUT / "survey_responses.csv", index=False)
    print(f"  {len(surveys):,} survey responses")

    print("Building manager_reinforcement...")
    mgr = build_manager_reinforcement(emp)
    mgr.to_csv(OUT / "manager_reinforcement.csv", index=False)
    print(f"  {len(mgr):,} manager-week records")

    print("Building champion_activity...")
    champ = build_champion_activity()
    champ.to_csv(OUT / "champion_activity.csv", index=False)
    print(f"  {len(champ):,} champion activity records")

    print("Building workflow_stories...")
    stories = build_workflow_stories()
    stories.to_csv(OUT / "workflow_stories.csv", index=False)
    print(f"  {len(stories):,} workflow stories")

    print("\nDone. Data written to:", OUT)


if __name__ == "__main__":
    main()
