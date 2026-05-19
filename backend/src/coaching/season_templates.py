"""Season report narrative templates.

Variables available:
- {season}: Season number completed
- {next_season}: Next season number
- {biggest_mover_name}: Pillar with largest improvement
- {biggest_mover_delta}: Points gained by biggest mover
- {biggest_mover_score}: Current score of biggest mover
- {weakest_name}: Lowest scoring pillar
- {weakest_score}: Score of weakest pillar
- {total_tasks_completed}: Total tasks completed in season
- {completion_rate}: Overall season completion rate
- {streak_best}: Longest streak achieved
- {score_start}: Optimisation score at season start
- {score_end}: Optimisation score at season end
- {score_delta}: Total score improvement
"""

OPENING_PARAGRAPHS: list[str] = [
    "Season {season} complete — 90 days of consistent improvement. Your FORGE Score moved from {score_start} to {score_end}, a {score_delta}-point improvement driven by {total_tasks_completed} completed tasks.",
    "You've finished Season {season}. Over 90 days, you completed {total_tasks_completed} tasks with a {completion_rate}% average completion rate, moving your optimisation score by {score_delta} points.",
    "Season {season} is done. From {score_start} to {score_end} — that's {score_delta} points of real, measurable improvement. {total_tasks_completed} tasks completed, {streak_best}-day best streak.",
]

BIGGEST_MOVER_PARAGRAPHS: list[str] = [
    "{biggest_mover_name} saw the largest improvement this season — up {biggest_mover_delta} points to {biggest_mover_score}. Your consistent focus here paid off with compounding returns.",
    "Your standout pillar: {biggest_mover_name} (+{biggest_mover_delta} to {biggest_mover_score}). The routine you built around this area created the strongest improvement curve.",
    "{biggest_mover_name} was your MVP pillar, climbing {biggest_mover_delta} points. The tasks in this area clearly resonated with your lifestyle and commitment level.",
]

NEEDS_WORK_PARAGRAPHS: list[str] = [
    "{weakest_name} at {weakest_score} has the most room to grow next season. This doesn't mean failure — it means opportunity. Targeted focus here will yield fast results.",
    "Your lowest pillar ({weakest_name}: {weakest_score}) becomes Season {next_season}'s biggest lever. Small gains here will disproportionately boost your overall score.",
    "{weakest_name} ({weakest_score}) represents untapped potential. Season {next_season} will include more targeted tasks for this area.",
]

NEXT_FOCUS_PARAGRAPHS: list[str] = [
    "Season {next_season} will build on your strengths while addressing gaps. Expect recalibrated weights, progressive task difficulty, and new pillar focus areas.",
    "Going into Season {next_season}: pillar weights recalibrate based on your progress. Tasks advance in difficulty. The compound effect accelerates from here.",
    "Season {next_season} starts fresh with updated scoring weights reflecting your growth. Your strongest pillars maintain while weaker ones get focused attention.",
]


"""
=== FILE FLOW DOCUMENTATION ===

Functionality: Season report narrative templates with data interpolation.

Flow:
1. Opening paragraph summarises the season stats
2. Biggest mover section highlights top-performing pillar
3. Needs work section identifies growth opportunities
4. Next focus previews the upcoming season

Main Entry Point: OPENING_PARAGRAPHS, BIGGEST_MOVER_PARAGRAPHS, etc.

Dependencies: None
"""
