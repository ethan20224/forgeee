"""Weekly report paragraph templates for coaching notes and focus areas.

Templates are keyed by (stage, context_type) where:
- stage: outcome/habit/mechanism
- context_type: "coaching" (main coaching paragraph) or "focus" (next week focus)

Variables available:
- {pillar_name}: Weakest or strongest pillar
- {score}: Pillar score
- {rate}: Weekly completion rate
- {week}: Current week number
- {streak}: Current streak
"""

COACHING_PARAGRAPHS: dict[tuple[str, str], list[str]] = {
    ("outcome", "low_completion"): [
        "This week's completion rate of {rate}% shows room to build momentum. Focus on the minimum viable routine — even 5 minutes of consistency compounds faster than sporadic longer sessions.",
        "At {rate}% completion, the priority is habit initiation rather than perfection. Start with the easiest task each morning to trigger the routine cascade.",
    ],
    ("outcome", "high_completion"): [
        "Strong week at {rate}% completion. You're proving that the routine fits your schedule. This early consistency predicts long-term success.",
        "{rate}% completion rate — exceptional for the first few weeks. The foundation is solid; results will begin compounding.",
    ],
    ("outcome", "pillar_weakness"): [
        "{pillar_name} is your current lowest pillar at {score}. The tasks this week specifically target this area — consistent execution will drive the fastest improvement here.",
        "Your {pillar_name} score of {score} represents your biggest opportunity. Small consistent actions in this pillar yield the most visible results.",
    ],
    ("habit", "low_completion"): [
        "Completion dipped to {rate}% this week. Habit formation requires a minimum threshold of consistency — identify which tasks are being skipped and simplify them.",
        "At {rate}% this week, consider whether the routine needs simplification. Remove friction from the hardest tasks rather than adding willpower.",
    ],
    ("habit", "high_completion"): [
        "{rate}% completion in the habit phase is excellent. The routine is becoming automatic — your brain is allocating less effort to these decisions.",
        "Week {week} at {rate}% — the habit loop is strengthening. You're past the resistance phase and into the momentum phase.",
    ],
    ("habit", "pillar_weakness"): [
        "{pillar_name} at {score} needs more attention. Stack the {pillar_name} tasks immediately after your most consistent existing habit.",
        "Your weakest pillar ({pillar_name}: {score}) benefits most from habit linking — attach its tasks to an existing trigger.",
    ],
    ("mechanism", "low_completion"): [
        "Completion at {rate}% this week. At this stage, selective focus on high-impact tasks yields better results than broad low-quality execution.",
        "{rate}% completion — consider whether you're experiencing routine fatigue. Introduce micro-variations to maintain engagement without losing consistency.",
    ],
    ("mechanism", "high_completion"): [
        "{rate}% completion on week {week}. At the mechanism stage, you're operating at peak efficiency — each task leverages accumulated knowledge.",
        "Exceptional {rate}% this week. The system is optimised — cross-pillar synergies are maximising returns on each task.",
    ],
    ("mechanism", "pillar_weakness"): [
        "{pillar_name} at {score} — this pillar may need a different approach. Advanced-tier tasks or increased frequency could break through the plateau.",
        "Your {pillar_name} score ({score}) may be hitting diminishing returns from current tasks. Consider intensity progression.",
    ],
}

FOCUS_PARAGRAPHS: dict[tuple[str, str], list[str]] = {
    ("outcome", "general"): [
        "Next week, prioritise visibility. Focus on tasks where you can see or feel results within days — skin and grooming offer the fastest feedback loops.",
        "For week {week}, anchor the morning routine first. Once the start-of-day trigger is automatic, everything else cascades more easily.",
    ],
    ("outcome", "pillar_focus"): [
        "Week {week} focus: {pillar_name}. Dedicate extra attention to this pillar — it has the highest potential for visible improvement right now.",
        "Next week, lean into {pillar_name} tasks. Early-stage improvements here will boost overall score and motivation.",
    ],
    ("habit", "general"): [
        "Next week, focus on streak maintenance. Every unbroken day strengthens the neural pathway. Protect the streak above adding new complexity.",
        "Week {week} priority: consistency over intensity. Complete all tasks at minimum effort rather than skipping any entirely.",
    ],
    ("habit", "pillar_focus"): [
        "Focus {pillar_name} next week. Link its tasks to your strongest existing habit — the anchor will pull this pillar into your automatic routine.",
        "Week {week}: double down on {pillar_name}. At the habit stage, focused repetition creates the strongest long-term patterns.",
    ],
    ("mechanism", "general"): [
        "Next week, audit your task quality. Are you executing with full attention, or going through the motions? Mechanism-stage gains come from precision.",
        "Week {week}: optimise timing. Match high-effort tasks to your peak energy window for maximum physiological benefit.",
    ],
    ("mechanism", "pillar_focus"): [
        "Focus: {pillar_name} intensity progression. You've mastered the basics — push into advanced techniques for breakthrough results.",
        "Week {week}: {pillar_name} optimisation. At this stage, marginal gains come from precision timing and technique refinement.",
    ],
}


"""
=== FILE FLOW DOCUMENTATION ===

Functionality: ~20 paragraph templates for weekly reports (coaching notes + focus areas).

Flow:
1. COACHING_PARAGRAPHS selected based on (stage, completion_context)
2. FOCUS_PARAGRAPHS selected based on (stage, focus_type)
3. Variables interpolated with weekly data

Main Entry Point: COACHING_PARAGRAPHS, FOCUS_PARAGRAPHS

Dependencies: None
"""
