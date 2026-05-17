# FORGE Documentation

## Project Summary

**FORGE** is a mobile application (React Native / Expo) that delivers a structured **90-day Season** appearance transformation program for men, powered by Codex AI (Claude). Users take a baseline photo, receive a personalised AI-generated plan drawn from a curated **Master Task Library** (~150 tasks), complete daily habit tasks, track progress every 3 days via AI vision photo check-ins, earn XP and streaks, and receive weekly AI coaching reports. The core metric is the **FORGE Optimisation Score** — a weighted composite 0–100 across 9 pillars that reflects the user's overall appearance improvement trajectory.

- **Platform**: iOS (primary), Android, Web
- **Tech**: Expo ~55, React Native 0.83, TypeScript 5.9, Supabase (PostgreSQL + Auth + Storage + Edge Functions), Codex AI (Claude Sonnet 4.6 via server-side proxy), RevenueCat (payments), PostHog (analytics)

## Current Status

**Phase**: MVP shipped. Onboarding redesign (F4) complete — baseline photo deferred to day 3. Repositioning copy (F5) complete. Creator outreach template (F3) created. All 17 database migrations applied. 5 edge functions deployed and cron-scheduled. 9-pillar scoring system active. Photo bucket privatised with signed URLs. Referral system live. PostHog analytics instrumented (7 events). Share card feature built.

**Active sprint**: Post-MVP polish — notification guilt-language removal, streak risk notification replacement, first-strike celebration modal, program day advancement hardening.

## Who Uses the System

| Role | Description |
|------|-------------|
| **User / Member** | A man who subscribed to FORGE. Completes daily tasks, takes 3-day photo check-ins, receives AI coaching. Tracked in `users` table with `onboarded=true`. |
| **Guest** | Unauthenticated visitor viewing welcome slides, quiz, and signup screens. Has no `users` row. Quiz answers cached locally as a draft. |
| **Admin / Operator** | Internal user with Supabase dashboard access. Monitors `rate_limits`, `claude_api_calls`, and `season_events` tables. No admin UI exists. |

## Document Index

### Foundation

| Document | Covers | MVP Status |
|----------|--------|------------|
| [glossary.md](glossary.md) | Every domain term defined across the system | ✅ Done |
| [personas.md](personas.md) | User personas with goals, pain points, behaviors | ✅ Done |
| [data-model.md](data-model.md) | Full database schema, indexes, ER diagram, query patterns | ✅ Done |
| [architecture.md](architecture.md) | Tech stack, project structure, subsystems, state machines, external integrations | ✅ Done |
| [design.md](design.md) | Design tokens, screen specs, user flows, UI components | ✅ Done |

### Feature Specifications

| Document | Covers | MVP Status |
|----------|--------|------------|
| [features/01-onboarding.md](features/01-onboarding.md) | Welcome → Quiz → Signup → Plan Generation → Plan Reveal → Paywall | ✅ Done |
| [features/02-daily-tasks.md](features/02-daily-tasks.md) | Task display, completion, XP, streak, home screen | ✅ Done |
| [features/03-cycle-checkins.md](features/03-cycle-checkins.md) | 3-day photo check-ins, Claude Vision analysis, cycle history | ✅ Done |
| [features/04-scoring.md](features/04-scoring.md) | 9-pillar scores, FORGE Optimisation Score, weights, face shape adjustments | ✅ Done |
| [features/05-coaching.md](features/05-coaching.md) | Daily insights, weekly reports, season reports, language stages | ✅ Done |
| [features/06-gamification.md](features/06-gamification.md) | XP, levels, streaks, challenges, badges, micro-sprints | ✅ Done |
| [features/07-subscription.md](features/07-subscription.md) | RevenueCat paywall, $11/mo Basic tier, purchase/restore flow | ✅ Done |
| [features/08-referrals.md](features/08-referrals.md) | Referral code generation, sharing, tracking | ✅ Done |
| [features/09-photo-management.md](features/09-photo-management.md) | Photo capture, crop, upload, private bucket, signed URLs, timeline | ✅ Done |
| [features/10-notifications.md](features/10-notifications.md) | Push scheduling, cycle prompts, weekly reports, day-1 push, guilt-free policy | ✅ Done |
| [features/11-share-cards.md](features/11-share-cards.md) | Social share card generation with scores and progress | ✅ Done |
| [features/12-profile-settings.md](features/12-profile-settings.md) | Profile screen, account deletion, sign out, settings | ✅ Done |
| [features/13-program-advancement.md](features/13-program-advancement.md) | Day advancement logic, season rollover, season-complete screen | ✅ Done |

### User Flows

| Document | Covers | MVP Status |
|----------|--------|------------|
| [flows/onboarding-flow.md](flows/onboarding-flow.md) | Complete onboarding journey: splash → welcome → quiz → signup → plan-loading → plan-reveal → paywall → app | ✅ Done |
| [flows/daily-routine-flow.md](flows/daily-routine-flow.md) | Daily task completion, XP, streak, insights | ✅ Done |
| [flows/cycle-checkin-flow.md](flows/cycle-checkin-flow.md) | 3-day photo check-in, AI analysis, before/after comparison | ✅ Done |
| [flows/season-complete-flow.md](flows/season-complete-flow.md) | Day 90 detection, season report, season rollover | ✅ Done |
| [flows/sign-in-flow.md](flows/sign-in-flow.md) | Returning user sign-in, auth state recovery, routing | ✅ Done |

### Planning

| Document | Covers | MVP Status |
|----------|--------|------------|
| [user-stories.md](user-stories.md) | All user stories organized by persona and feature area | ✅ Done |
| [edge-cases.md](edge-cases.md) | Edge cases, open questions, resolved decisions | ✅ Done |
| [roadmap.md](roadmap.md) | Phased delivery plan (MVP / Phase 2 / Phase 3) | ✅ Done |

---

## Delivery Phases at a Glance

**MVP**: A man downloads FORGE, completes a 7-question quiz about his goals and current routine, creates an account, and instantly receives a personalised 90-day plan generated by Codex AI from a curated task library. He pays $11/mo, unlocks the app, and on day 3 takes a baseline photo. Every day he completes 2–5 short tasks (5–60 min) spanning skin, grooming, style, posture, and more. Every 3 days he takes progress photos — Codex Vision analyses them, scores each of 9 pillars, and surfaces the biggest mover. He earns XP, builds streaks, and unlocks badges. Every Sunday he gets an AI-generated coaching report. At day 90 his season ends with a story-formatted report comparing his before/after scores, identifying habits that stuck, and setting focus for Season 2.

**Phase 2** (planned): Advanced cohort features — social sharing improvements, creator/influencer partnerships, analytics dashboard, advanced plan customisation.

**Phase 3** (planned): AI-powered micro-sprint engine, voice-guided workouts, hardware integration (smart mirrors), enterprise/team plans.

---

## Key Design Principles

- **Pillar-first everything** — The 9 pillars are the atomic unit of measurement, coaching, and plan structure. Every task maps to a pillar. Every score change is pillar-granular. Every coaching insight references pillar movement. This creates a consistent, composable system.

- **AI is a tool, not the product** — Codex generates plans and analyses photos, but the Master Task Library is the source of truth. Codex selects from curated tasks — it never invents them. This keeps quality predictable and prevents AI drift.

- **Flat dark surfaces, no shadows** — The visual language uses deep charcoal (`#141414`) with opacity-bordered cards. No drop shadows. Teal (`#00C4A7`) for scores only, gold (`#E8A400`) for CTAs only. Inter font, strict type scale.

- **Onboarding defers friction** — Baseline photo is no longer required during signup. It's prompted on day 3 when the user is invested. Quiz happens before account creation — answers are cached locally as a draft so the user sees value before committing.

- **Every screen handles 3 states** — Loading (skeleton/spinner), content (data present), and empty/error (actionable message with retry). No screen renders a blank white state.

- **Notifications use factual reassurance, never guilt** — "Cycle photo today. Same angle, same lighting." Not "Your streak is at risk! Come back!" No urgency, no FOMO, no shaming.

---

## Open Questions Remaining

| ID | Question | Blocks |
|----|----------|--------|
| OQ-01 | Should the task library be expandable by admin without code changes? | Phase 2 content management |
| OQ-02 | Should face shape be re-detected on every cycle check-in, or only on baseline? | Score accuracy for users whose face changes significantly |
| OQ-03 | Should XP/levels reset on season rollover or persist across seasons? | Season 2 gamification design |
| OQ-04 | Should micro-sprints be user-initiated, AI-initiated, or both? | Phase 2 micro-sprint engine |
| OQ-05 | Should the plan be regeneratable mid-season if the user's situation changes? | Plan flexibility feature |
| OQ-06 | What is the exact trigger for "streak at risk" — should it be 2 days or configurable? | Notification policy (currently: guilt-free, no risk notifications) |
| OQ-07 | Should subscription tier gating be reintroduced for Phase 2 features? | Phase 2 monetization strategy |
