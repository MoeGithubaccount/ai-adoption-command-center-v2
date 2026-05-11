# AI Adoption Command Center

A decision system for AI enablement teams. Takes the signals most organizations
already have — usage telemetry, support tickets, training records, surveys,
manager check-ins — and converts them into a prioritized queue of specific
support actions.

The dashboard ends in an **Intervention Queue**: for each function showing
weak adoption, the most likely diagnosis, the recommended intervention, the
owner, the playbook, the follow-up window, and the success signal to watch.

## The five-stage loop

```
Signal → Diagnosis → Intervention → Playbook → Success Signal
```

Most adoption dashboards stop at the first step. This one runs the loop.

## What this is

A working demo on synthetic data for a fictional 4,200-person organization
(Northstar Enterprise Services), modeled on patterns drawn from:

- Microsoft Copilot Dashboard / Viva Insights documentation
- Microsoft 365 Copilot adoption report (Power BI template)
- Microsoft Work Trend Index (2025, 2026)
- McKinsey *State of AI in 2025*
- Deloitte *State of Generative AI in the Enterprise*
- ServiceNow AI Control Tower documentation
- Cornell research on algorithmic monitoring and workplace resistance (Zitek et al., 2024)
- Pew Research Center: *Americans' Views on Use of AI to Monitor and Evaluate Workers*

## What this is not

- Not a usage analytics platform.
- Not a governance or compliance tool.
- Not an employee monitoring system.
- Not a replacement for Microsoft Copilot Dashboard. It consumes the kind of signal that platform produces.

## Responsible tracking, designed in

Every signal in this dashboard is evaluated against one test:

> Does this point to a support action, or to an individual judgment?

Signals that fail the test do not appear in the product.

Hard rules:

- **Cohort-level only.** Minimum cohort size of 10. Smaller cohorts are suppressed.
- **No individual prompt content.** Never stored, never analyzed, never surfaced.
- **No per-user usage as a performance signal.** No part of this system feeds into reviews.
- **Themes, not message text.** Support friction is clustered by theme tag.
- **Manager reinforcement is self-reported.** Never inferred from communication content.
- **Workflow change stories are voluntary** and anonymized.

The Responsible Tracking page in the app names every line.

## Run locally

```bash
pip install -r requirements.txt
python data/generate_data.py
streamlit run app.py
```

The data generator produces nine CSV files in `data/`. The app reads them
on startup and caches them. To regenerate (with different random seed),
edit `RNG = np.random.default_rng(42)` in `data/generate_data.py`.

## Project structure

```
ai-adoption-command-center/
├── app.py                          # Executive Snapshot (home)
├── pages/
│   ├── 1_Adoption_Health.py        # Function-level signals
│   ├── 2_Training_Impact.py        # Training-to-usage lift (stub)
│   ├── 3_Support_Friction.py       # Theme clusters
│   ├── 4_Trust_and_Verification.py # Cohort confidence + verify
│   ├── 5_Workflow_Value.py         # Stories + would-they-miss-it
│   ├── 6_Adoption_Diagnosis.py     # Per-function diagnoses
│   ├── 7_Intervention_Queue.py     # The centerpiece
│   └── 8_Responsible_Tracking.py   # Principles, not a footer
├── data/                           # Synthetic data + generator
├── lib/
│   ├── loaders.py
│   ├── diagnostics.py
│   ├── interventions.py
│   └── theme.py
└── requirements.txt
```

## Deploy

Streamlit Community Cloud, free tier. Connect the GitHub repo, point at
`app.py`, set `requirements.txt`, deploy.

## Limits

This is a portfolio prototype. The synthetic data is designed to look like
plausible enterprise telemetry, including realistic noise and contradictions
(IT has high usage but low would-miss-it; Research has high usage but low
verification scores; Customer Support shows an intervention bump in month 5).
No real organization is modeled. No real signals are claimed.

The intervention library ships with eight pattern→intervention mappings.
A production version would have more, and would calibrate thresholds against
the organization's own baselines rather than the defaults here.

The training-to-usage lift analysis is structured but not implemented in this
version. The page describes the intended approach: matched cohort, 4-week
baseline, 12-week tracking, bootstrap CI.

## Author

Built by Mo Ibrahim. Portfolio project for roles in AI Enablement,
Microsoft 365 Copilot Adoption, Digital Workplace, AI Support Operations,
Responsible AI Enablement, and GenAI Change Management.
