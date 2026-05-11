"""Cached data loaders. All access is cohort-level only."""

from pathlib import Path
import pandas as pd
import streamlit as st

DATA = Path(__file__).parent.parent / "data"

MIN_COHORT_SIZE = 10  # Hard floor. Cohorts smaller than this are suppressed everywhere.


@st.cache_data
def load_employees():
    return pd.read_csv(DATA / "employees.csv", parse_dates=["license_assigned_date"])


@st.cache_data
def load_usage_weekly():
    return pd.read_csv(DATA / "usage_weekly.csv", parse_dates=["week_start"])


@st.cache_data
def load_tickets():
    return pd.read_csv(DATA / "support_tickets.csv", parse_dates=["week"])


@st.cache_data
def load_surveys():
    return pd.read_csv(DATA / "survey_responses.csv", parse_dates=["month"])


@st.cache_data
def load_manager_reinforcement():
    return pd.read_csv(DATA / "manager_reinforcement.csv", parse_dates=["week"])


@st.cache_data
def load_training():
    events = pd.read_csv(DATA / "training_events.csv", parse_dates=["date"])
    attendance = pd.read_csv(DATA / "training_attendance.csv")
    return events, attendance


@st.cache_data
def load_champions():
    return pd.read_csv(DATA / "champion_activity.csv", parse_dates=["week"])


@st.cache_data
def load_stories():
    return pd.read_csv(DATA / "workflow_stories.csv", parse_dates=["week"])


def department_health(usage, employees, ref_week=None):
    """Compute department-level adoption health, cohort-suppressed."""
    licensed = employees[employees.copilot_licensed].groupby("department").size().rename("licensed")
    if ref_week is None:
        ref_week = usage.week_start.max()

    window = usage[usage.week_start >= ref_week - pd.Timedelta(weeks=6)]
    active_6w = window.groupby(["department", "employee_id"]).size().reset_index(name="weeks_active")
    sustained = (active_6w.weeks_active >= 4).groupby(active_6w.department).sum().rename("sustained_users")

    out = pd.concat([licensed, sustained], axis=1).fillna(0)
    out["sustained_rate"] = (out.sustained_users / out.licensed).fillna(0)
    out = out[out.licensed >= MIN_COHORT_SIZE]  # suppress small cohorts
    return out.reset_index()
