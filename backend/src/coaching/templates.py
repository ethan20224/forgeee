"""Daily insight templates keyed by (stage, context_type, pillar).

Each template uses {variable} interpolation for dynamic data:
- {pillar_name}: Display name of the affected pillar
- {score}: Current pillar score
- {delta}: Score change (absolute value)
- {streak}: Current streak count
- {rate}: Completion rate percentage
- {day}: Current program day
"""

DAILY_INSIGHT_TEMPLATES: dict[tuple[str, str, str | None], list[str]] = {
    # --- OUTCOME STAGE (days 1-14): Focus on visible results ---
    ("outcome", "pillar_up", "skin"): [
        "Skin clarity improved {delta} points this cycle. UV protection and hydration are compounding.",
        "Your skin score moved to {score}. Consistent cleansing breaks down buildup over 21-day cycles.",
        "Skin at {score} — the daily routine is already showing. Cell turnover takes 28 days to fully reflect.",
    ],
    ("outcome", "pillar_up", "hair"): [
        "Hair score up {delta} points. Scalp stimulation increases follicle blood flow within the first week.",
        "Hair at {score}. The styling adjustments are framing your face better already.",
    ],
    ("outcome", "pillar_up", "grooming"): [
        "Grooming score hit {score}. Sharp lines and clean edges signal attention to detail.",
        "Grooming improved {delta} points. Consistent eyebrow and facial hair maintenance compounds fast.",
    ],
    ("outcome", "pillar_up", "posture"): [
        "Posture improved {delta} points. Shoulder alignment affects how others perceive your frame.",
        "Posture at {score}. Chin tucks and wall stands are already adjusting your neutral alignment.",
    ],
    ("outcome", "pillar_up", "style"): [
        "Style score reached {score}. Fit and colour coordination make the biggest early impact.",
        "Style up {delta} points. Small wardrobe adjustments create outsized visual improvements.",
    ],
    ("outcome", "pillar_up", "sleep"): [
        "Sleep score at {score}. Consistent wind-down routines are improving recovery markers.",
        "Sleep improved {delta} points. Blue light reduction before bed accelerates melatonin onset.",
    ],
    ("outcome", "pillar_up", "nutrition"): [
        "Nutrition at {score}. Hydration and anti-inflammatory foods reduce facial puffiness within days.",
        "Nutrition up {delta} points. Water retention drops are already visible in your facial structure.",
    ],
    ("outcome", "pillar_up", "facial_composition"): [
        "Facial composition at {score}. Mewing and jaw exercises show subtle changes in the first weeks.",
        "Facial structure improved {delta} points. Posture and jaw positioning work synergistically.",
    ],
    ("outcome", "pillar_up", "voice"): [
        "Voice score at {score}. Resonance exercises are building tonal depth.",
        "Voice improved {delta} points. Diaphragmatic breathing creates a fuller vocal presence.",
    ],
    ("outcome", "pillar_down", None): [
        "{pillar_name} dipped {delta} points. This is normal fluctuation — consistency reverses it within a cycle.",
        "{pillar_name} dropped to {score}. One off day doesn't erase progress. Focus on today's tasks.",
    ],
    ("outcome", "streak_milestone", None): [
        "{streak}-day streak! You're building the foundation. The first two weeks establish the baseline.",
        "{streak} days in. Early consistency is the hardest part — you're past the initial friction.",
    ],
    ("outcome", "completion_rate", None): [
        "{rate}% completion rate today. Each completed task moves you closer to visible results.",
        "Day {day}: {rate}% done. Momentum builds when you see the daily progress.",
    ],
    # --- HABIT STAGE (days 15-30): Focus on routine and consistency ---
    ("habit", "pillar_up", "skin"): [
        "Skin at {score}. The routine is becoming automatic — this is where compound returns begin.",
        "Skin improved {delta} points. Two weeks of consistency means your skin barrier is strengthening.",
    ],
    ("habit", "pillar_up", "hair"): [
        "Hair at {score}. Your scalp routine is past the adjustment period — results accelerate from here.",
        "Hair up {delta}. Consistent product application builds cumulative strand protection.",
    ],
    ("habit", "pillar_up", "grooming"): [
        "Grooming at {score}. The maintenance rhythm is locked in — sharpness becomes effortless.",
        "Grooming improved {delta}. Autopilot routines free mental energy for other pillars.",
    ],
    ("habit", "pillar_up", "posture"): [
        "Posture at {score}. Muscle memory is forming — your neutral stance is shifting permanently.",
        "Posture up {delta}. The correction cues are becoming subconscious triggers.",
    ],
    ("habit", "pillar_up", "style"): [
        "Style at {score}. Your outfit formulas are reducing decision fatigue while improving presentation.",
        "Style improved {delta}. Consistent fit choices signal intentional self-care.",
    ],
    ("habit", "pillar_up", "sleep"): [
        "Sleep at {score}. Your circadian rhythm is stabilising — recovery quality improves each week.",
        "Sleep up {delta}. The wind-down ritual is now a habit — cortisol levels drop faster.",
    ],
    ("habit", "pillar_up", "nutrition"): [
        "Nutrition at {score}. Your hydration habit is reducing inflammation markers visibly.",
        "Nutrition improved {delta}. Consistent protein intake supports collagen synthesis for skin.",
    ],
    ("habit", "pillar_up", "facial_composition"): [
        "Facial composition at {score}. Daily exercises are building muscle memory in jaw positioning.",
        "Facial structure up {delta}. Consistency in mewing creates structural adaptation over weeks.",
    ],
    ("habit", "pillar_up", "voice"): [
        "Voice at {score}. Daily practice is building the neural pathways for richer tone.",
        "Voice up {delta}. Resonance improves most between weeks 2-4 of consistent practice.",
    ],
    ("habit", "pillar_down", None): [
        "{pillar_name} dipped {delta} points. Revisit the evening routine — consistency anchors progress.",
        "{pillar_name} at {score}. A small setback in the habit phase is temporary. Re-anchor tomorrow.",
    ],
    ("habit", "streak_milestone", None): [
        "{streak}-day streak. The routine is becoming automatic — completion rate is {rate}%.",
        "{streak} days strong. You're past the habit formation threshold. This is now who you are.",
    ],
    ("habit", "completion_rate", None): [
        "{rate}% completion. The habit loop is strengthening — each day reinforces the next.",
        "Day {day}: {rate}% done. Habit stacking is compounding across multiple pillars.",
    ],
    # --- MECHANISM STAGE (days 31+): Focus on science and mechanisms ---
    ("mechanism", "pillar_up", "skin"): [
        "Skin at {score}. Retinoid application accelerates epidermal turnover by binding RAR receptors.",
        "Skin improved {delta}. At this stage, ceramide production has normalised — barrier function is peak.",
        "Skin at {score}. Niacinamide is reducing sebaceous activity while strengthening the lipid barrier.",
    ],
    ("mechanism", "pillar_up", "hair"): [
        "Hair at {score}. DHT-blocking compounds are protecting follicles at the dermal papilla level.",
        "Hair up {delta}. Scalp massage increases perfusion — nutrients reach follicles more efficiently.",
    ],
    ("mechanism", "pillar_up", "grooming"): [
        "Grooming at {score}. Precision in maintenance reduces micro-trauma to hair follicles.",
        "Grooming improved {delta}. The systematic approach minimises skin irritation from repeated styling.",
    ],
    ("mechanism", "pillar_up", "posture"): [
        "Posture at {score}. Deep cervical flexor activation is rebalancing upper crossed syndrome.",
        "Posture up {delta}. Thoracic extension exercises counter forward head posture at the root.",
    ],
    ("mechanism", "pillar_up", "style"): [
        "Style at {score}. Colour theory application — contrasting values draw attention to facial features.",
        "Style improved {delta}. Proportion-aware dressing creates visual length and structure.",
    ],
    ("mechanism", "pillar_up", "sleep"): [
        "Sleep at {score}. Consistent circadian rhythm maximises HGH release during deep sleep phases.",
        "Sleep up {delta}. Temperature regulation during sleep optimises REM cycle length.",
    ],
    ("mechanism", "pillar_up", "nutrition"): [
        "Nutrition at {score}. Omega-3 fatty acids reduce systemic inflammation — visible in skin clarity.",
        "Nutrition improved {delta}. Collagen peptide intake supports dermal matrix density.",
    ],
    ("mechanism", "pillar_up", "facial_composition"): [
        "Facial composition at {score}. Masseter engagement during mewing redistributes hyoid bone tension.",
        "Facial structure up {delta}. Consistent tongue posture influences maxillary development over months.",
    ],
    ("mechanism", "pillar_up", "voice"): [
        "Voice at {score}. Laryngeal tilt exercises increase harmonic richness in the vocal signal.",
        "Voice improved {delta}. Pharyngeal space expansion creates natural resonance amplification.",
    ],
    ("mechanism", "pillar_down", None): [
        "{pillar_name} at {score}. Temporary regression often precedes adaptation — the system is recalibrating.",
        "{pillar_name} dipped {delta}. Score variance is expected — the trend line matters more than any single point.",
    ],
    ("mechanism", "streak_milestone", None): [
        "{streak}-day streak. Neuroplastic adaptation is complete — the routine is hardwired.",
        "{streak} days. At this stage, habit execution requires minimal prefrontal engagement.",
    ],
    ("mechanism", "completion_rate", None): [
        "{rate}% completion on day {day}. System efficiency is high — each task compounds previous gains.",
        "Day {day}: {rate}% done. The integration phase maximises cross-pillar synergies.",
    ],
}


def get_template_keys() -> list[tuple[str, str, str | None]]:
    """Return all available template keys for validation."""
    return list(DAILY_INSIGHT_TEMPLATES.keys())


"""
=== FILE FLOW DOCUMENTATION ===

Functionality: ~60 daily insight templates keyed by (language_stage, context_type, pillar).

Flow:
1. Templates selected by coaching service based on user state
2. Variables interpolated with real data ({score}, {delta}, etc.)
3. Rotation tracked per user to avoid repetition

Main Entry Point: DAILY_INSIGHT_TEMPLATES dict

Dependencies: None
"""
