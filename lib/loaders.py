from pathlib import Path
import runpy

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

REQUIRED_FILES = [
    "employees.csv",
    "usage_weekly.csv",
    "training_events.csv",
    "training_attendance.csv",
    "support_tickets.csv",
    "surveys.csv",
    "manager_reinforcement.csv",
    "champion_activity.csv",
    "workflow_stories.csv",
]


def ensure_generated_data():
    """
    Generate the synthetic CSV files if they are missing.

    The public app uses synthetic data only. This function runs data/generate_data.py
    on first deploy/cold start if the generated CSVs were not uploaded to GitHub.
    """
    DATA.mkdir(exist_ok=True)

    missing = [name for name in REQUIRED_FILES if not (DATA / name).exists()]
    if not missing:
        return

    generator = DATA / "generate_data.py"

    if not generator.exists():
        st.error(
            "Synthetic data files are missing, and data/generate_data.py was not found. "
            "Upload either the generated CSV files or the generate_data.py file."
        )
        st.stop()

    # Run the synthetic data generator. It should write CSVs into the data/ folder.
    runpy.run_path(str(generator), run_name="__main__")

    still_missing = [name for name in REQUIRED_FILES if not (DATA / name).exists()]
    if still_missing:
        st.error(
            "The synthetic data generator ran, but some expected files were still missing: "
            + ", ".join(still_missing)
        )
        st.stop()


def read_csv(filename, parse_dates=None):
    ensure_generated_data()
    return pd.read_csv(DATA / filename, parse_dates=parse_dates or [])


@st.cache_data
def load_employees():
    return read_csv("employees.csv", parse_dates=["license_assigned_date"])


@st.cache_data
def load_usage_weekly():
    return read_csv("usage_weekly.csv", parse_dates=["week_start"])


@st.cache_data
def load_training_events():
    return read_csv("training_events.csv", parse_dates=["date"])


@st.cache_data
def load_training_attendance():
    return read_csv("training_attendance.csv")


@st.cache_data
def load_support_tickets():
    return read_csv("support_tickets.csv", parse_dates=["week"])


@st.cache_data
def load_surveys():
    return read_csv("surveys.csv", parse_dates=["month"])


@st.cache_data
def load_manager_reinforcement():
    return read_csv("manager_reinforcement.csv", parse_dates=["week"])


@st.cache_data
def load_champion_activity():
    return read_csv("champion_activity.csv", parse_dates=["week"])


@st.cache_data
def load_workflow_stories():
    return read_csv("workflow_stories.csv", parse_dates=["week"])

@st.cache_data
def load_tickets():
    return load_support_tickets()
