"""Diagnosis to intervention mapping. The intervention library."""

LIBRARY = {
    "Reinforcement gap": {
        "intervention": "Manager Reinforcement Guide + director conversation",
        "owner": "Enablement Specialist + Function Director",
        "priority_default": "P1",
        "playbook": "manager_reinforcement_guide.md",
        "follow_up_days": 45,
        "success_signal": "Manager band moves to occasional+ within 45 days; sustained active rate +5 pts at 60 days.",
    },
    "Governance uncertainty": {
        "intervention": "Function-specific governance Q&A session + one-page data handling guide",
        "owner": "Enablement + IT Security",
        "priority_default": "P1",
        "playbook": "governance_qa_pack.md",
        "follow_up_days": 30,
        "success_signal": "Governance-fear theme down 40% in 30 days.",
    },
    "Tool confusion": {
        "intervention": "Publish 'Which AI tool when' one-pager; add to support ticket macros",
        "owner": "Enablement Specialist",
        "priority_default": "P2",
        "playbook": "tool_selector.md",
        "follow_up_days": 30,
        "success_signal": "Tool-selection theme down 30% in 30 days.",
    },
    "Verification gap": {
        "intervention": "Verification Habits workshop + checklist for the function",
        "owner": "Enablement Specialist",
        "priority_default": "P1",
        "playbook": "verification_habits.md",
        "follow_up_days": 30,
        "success_signal": "Verify-outputs score +0.7 pts at 60 days.",
    },
    "Workflow mismatch (low-stakes only)": {
        "intervention": "Workflow Fit interviews with 5 power users; pilot 2 high-stakes workflows",
        "owner": "Enablement Specialist",
        "priority_default": "P2",
        "playbook": "workflow_fit_audit.md",
        "follow_up_days": 90,
        "success_signal": "Would-they-miss-it +1.0 pts at 90 days; 3 high-stakes workflow stories captured.",
    },
    "Curiosity-not-habit": {
        "intervention": "Workflow coaching for the cohort; named-workflow office hours",
        "owner": "Enablement Specialist",
        "priority_default": "P2",
        "playbook": "workflow_coaching.md",
        "follow_up_days": 60,
        "success_signal": "Week 6 retention >50% at 60 days.",
    },
    "Awareness and provisioning gap": {
        "intervention": "Function kickoff session + license review with IT",
        "owner": "IT + Enablement",
        "priority_default": "P3",
        "playbook": "function_kickoff.md",
        "follow_up_days": 60,
        "success_signal": "Active rate >20% at 60 days; license coverage doubled.",
    },
    "No strong diagnostic signal": {
        "intervention": "Continue monitoring; no action recommended",
        "owner": "Enablement Specialist",
        "priority_default": "P3",
        "playbook": None,
        "follow_up_days": 30,
        "success_signal": "Patterns remain within normal range.",
    },
}


def intervention_for(diagnosis_name):
    return LIBRARY.get(diagnosis_name, LIBRARY["No strong diagnostic signal"])
