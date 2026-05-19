# FORGE — Architecture Plan

> Redesigned architecture for the FORGE male appearance transformation app.
> Priorities: security, cross-platform (web + Android + iOS), minimal cost, DeepSeek LLM.
> Last updated: 2026-05-19

---

## 1. Design Pillars

1. **Secure** — LLM keys server-side only, JWT auth, signed URLs, rate limiting at the API layer
2. **Cross-platform** — single codebase targeting iOS, Android, and web browsers
3. **Minimal cost** — deterministic logic replaces LLM wherever possible, self-hostable infra
4. **DeepSeek** — V4-Flash for text generation, VL2 for photo/vision analysis

---

## 2. Tech Stack

| Layer | Technology | Notes |
|---|---|---|
| **Frontend (mobile)** | Expo ~55, React Native 0.83, TypeScript | iOS + Android via EAS builds |
| **Frontend (web)** | React Native Web (via Expo) | Same codebase, exported for web |
| **Backend API** | FastAPI (Python 3.12+) | Async, Pydantic v2 validation, single API for all clients |
| **Database (dev)** | PostgreSQL 16 (local via Docker) | `docker compose up` for local dev |
| **Database (prod)** | PostgreSQL (Neon / Supabase / Railway) | Cloud-hosted, free tiers available, easy migration |
| **Auth** | FastAPI + python-jose + passlib (JWT) | Self-contained, no vendor dependency |
| **Object storage** | Cloudflare R2 | Zero egress fees, S3-compatible API |
| **LLM (text)** | DeepSeek V4-Flash API | Plan generation, coaching text |
| **LLM (vision)** | DeepSeek VL2 (via Replicate or DeepSeek API) | Photo analysis for cycle check-ins |
| **Payments (mobile)** | RevenueCat | Apple/Google in-app purchases |
| **Payments (web)** | Stripe | Web-only subscription checkout |
| **Analytics** | PostHog (cloud free tier) | 7 event types, generous free tier |
| **Push notifications** | Expo Push + Firebase FCM | Free, cross-platform |
| **Background jobs** | APScheduler (in-process) or pg_cron | Weekly reports, season rollover |
| **Hosting** | Fly.io or Railway | $5-7/mo for FastAPI + scheduled jobs |

---

## 3. DeepSeek Model Usage

### Models

| Model | Use Case | Pricing (per 1M tokens) |
|---|---|---|
| **DeepSeek V4-Flash** | Plan generation from quiz + task library | Input: $0.14 (miss) / $0.0028 (hit), Output: $0.28 |
| **DeepSeek VL2** | Cycle photo analysis (vision) | ~$0.01/run on Replicate or $0.15/1M tokens on SiliconFlow |

### LLM Call Points (After Optimisation)

| Feature | LLM? | Model | Frequency/Season | Notes |
|---|---|---|---|---|
| Plan generation | **Yes** | V4-Flash | 1x | Creative task, needs LLM. Cache by quiz-answer hash. |
| Photo analysis | **Yes** | VL2 | ~30x | Vision analysis irreplaceable. Every 3-day cycle. |
| Daily insight | **No** | — | 0 | Deterministic template engine (see section 7). |
| Weekly report | **No** | — | 0 | Deterministic template with data interpolation. |
| Season report | **No** | — | 0 | Deterministic template with before/after data fill. |
| Onboarding compliment | **No** | — | 0 | Template: "Your {best_pillar} shows strong foundations at {score}." |
| Quiz score estimate | **No** | — | 0 | Already deterministic (kept as-is). |

### Cost Estimate Per User Per Season (90 Days)

| Call | Count | Cost/Call | Subtotal |
|---|---|---|---|
| Plan generation (V4-Flash) | 1 | ~$0.005 | $0.005 |
| Photo analysis (VL2 via Replicate) | 30 | ~$0.01 | $0.30 |
| **Total LLM cost per user/season** | | | **~$0.31** |

Compared to current Claude architecture (~$3-5/user/season), this is a **90-95% reduction**.

---

## 4. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENTS                              │
│                                                             │
│  ┌───────────┐   ┌───────────┐   ┌───────────────────────┐ │
│  │  iOS App  │   │ Android   │   │   Web Browser         │ │
│  │  (Expo)   │   │  (Expo)   │   │   (React Native Web)  │ │
│  └─────┬─────┘   └─────┬─────┘   └──────────┬────────────┘ │
│        └────────────────┴────────────────────┘              │
│                         │                                   │
│                   HTTPS JSON API                            │
│                  (JWT Bearer Token)                          │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    FastAPI Backend                           │
│                   (Python 3.12+)                            │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                   Middleware                          │   │
│  │  JWT Auth · Rate Limiter · CORS · Request Logging    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────┐  ┌───────────────┐  ┌─────────────────┐  │
│  │ Auth Router  │  │ Plan Router   │  │ Cycle Router    │  │
│  │              │  │               │  │                 │  │
│  │ POST /signup │  │ POST /generate│  │ POST /upload    │  │
│  │ POST /login  │  │ GET /current  │  │ POST /analyse   │  │
│  │ POST /refresh│  │               │  │ GET /history    │  │
│  │ DELETE /acct │  │ (DeepSeek     │  │                 │  │
│  │              │  │  V4-Flash)    │  │ (DeepSeek VL2)  │  │
│  └──────────────┘  └───────────────┘  └─────────────────┘  │
│                                                             │
│  ┌──────────────┐  ┌───────────────┐  ┌─────────────────┐  │
│  │ Task Router  │  │ Progress      │  │ Coaching Router │  │
│  │              │  │ Router        │  │                 │  │
│  │ GET /today   │  │               │  │ GET /insight    │  │
│  │ POST /done   │  │ GET /scores   │  │ GET /weekly     │  │
│  │ GET /heatmap │  │ GET /streak   │  │ GET /season     │  │
│  │              │  │               │  │                 │  │
│  │ (determin.)  │  │ (determin.)   │  │ (TEMPLATES —    │  │
│  │              │  │               │  │  no LLM calls)  │  │
│  └──────────────┘  └───────────────┘  └─────────────────┘  │
│                                                             │
│  ┌──────────────┐  ┌───────────────┐  ┌─────────────────┐  │
│  │ Subscription │  │ Notification  │  │ Scheduler       │  │
│  │ Router       │  │ Service       │  │                 │  │
│  │              │  │               │  │ Season rollover │  │
│  │ RevenueCat   │  │ Expo Push /   │  │ Weekly report   │  │
│  │ webhook +    │  │ FCM           │  │ gen (template)  │  │
│  │ Stripe hook  │  │               │  │ Streak check    │  │
│  └──────────────┘  └───────────────┘  └─────────────────┘  │
│                                                             │
└─────────┬──────────────────────┬────────────────────────────┘
          │                      │
    ┌─────▼──────────┐    ┌──────▼──────────┐
    │  PostgreSQL     │    │  Cloudflare R2  │
    │                 │    │  (photos)       │
    │  DEV:  Docker   │    │                 │
    │  PROD: Neon /   │    │  Zero egress    │
    │    Supabase /   │    │  S3-compatible  │
    │    Railway      │    │  Presigned URLs │
    └─────────────────┘    └─────────────────┘
```

---

## 5. API Endpoints

### Auth (`/api/v1/auth`)

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/signup` | Public | Email + password signup, returns JWT pair |
| POST | `/login` | Public | Email + password login, returns JWT pair |
| POST | `/refresh` | Refresh token | Issue new access token |
| DELETE | `/account` | Bearer | Delete account + all user data |

### Users (`/api/v1/users`)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/me` | Bearer | Current user profile |
| PATCH | `/me` | Bearer | Update profile fields |

### Quiz (`/api/v1/quiz`)

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/submit` | Bearer | Save quiz answers |
| GET | `/estimate-score` | Bearer | Deterministic score estimate from answers |

### Plans (`/api/v1/plans`)

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/generate` | Bearer | Generate 90-day plan via DeepSeek V4-Flash. Rate: 2/hr. |
| GET | `/current` | Bearer | Get active plan for current season |
| GET | `/{plan_id}` | Bearer | Get specific plan |

### Tasks (`/api/v1/tasks`)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/today` | Bearer | Today's tasks for current program day |
| POST | `/{task_id}/complete` | Bearer | Mark task done, award XP, apply drift |
| GET | `/heatmap` | Bearer | 90-day completion grid |

### Cycles (`/api/v1/cycles`)

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/upload-url` | Bearer | Get presigned R2 upload URL |
| POST | `/analyse` | Bearer | Trigger DeepSeek VL2 analysis. Rate: 5/hr. |
| GET | `/history` | Bearer | All cycle records, newest first |
| GET | `/{cycle_id}` | Bearer | Single cycle detail |
| GET | `/compare/{a}/{b}` | Bearer | Side-by-side comparison of two cycles |

### Progress (`/api/v1/progress`)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/` | Bearer | Pillar scores, streak, XP, level, optimisation score |
| GET | `/pillar/{pillar}` | Bearer | Single pillar deep-dive with history |

### Coaching (`/api/v1/coaching`)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/daily-insight` | Bearer | Deterministic daily insight (template engine) |
| GET | `/weekly-report/{week}` | Bearer | Deterministic weekly report (template + data) |
| GET | `/weekly-reports` | Bearer | List all weekly reports |
| GET | `/season-report` | Bearer | Deterministic season report (template + data) |

### Subscriptions (`/api/v1/subscriptions`)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/status` | Bearer | Current subscription tier + expiry |
| POST | `/revenuecat-webhook` | Webhook secret | RevenueCat server events |
| POST | `/stripe-webhook` | Webhook secret | Stripe server events (web) |

### Gamification (`/api/v1/gamification`)

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/achievements` | Bearer | Unlocked badges |
| GET | `/challenges` | Bearer | Active + completed challenges |
| GET | `/streak` | Bearer | Current streak, longest, milestones |

### Share (`/api/v1/share`)

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/generate-card` | Bearer | Generate share card image server-side |

---

## 6. Database Schema

### Environment Setup

**Development:**
```bash
# docker-compose.yml provides PostgreSQL 16
docker compose up -d db
# Alembic runs migrations
alembic upgrade head
```

**Production:**
- Neon (free tier: 0.5 GB storage, autoscaling) — recommended for early stage
- Supabase (free tier: 500 MB, 2 GB bandwidth)
- Railway ($5/mo for 1 GB)

### Tables (14 tables — simplified from 16)

```
users                    # Core user profile + subscription + program state
quiz_answers             # 7-question quiz responses
plans                    # AI-generated 90-day plans (raw_json JSONB)
plan_cache               # NEW: quiz-answer hash → cached plan (avoids re-generation)
daily_tasks              # All 90 days of tasks per plan
task_library_selections  # Which library tasks were selected per plan
progress                 # Single row per user: 9 pillar scores, XP, streak
cycles                   # Photo check-in records with 9 pillar scores
achievements             # Unlocked badges
challenge_progress       # Active/completed challenges
weekly_reports           # Generated weekly reports (template output)
micro_sprints            # Event-driven sprint overrides
season_events            # Audit log for season transitions
pending_task_effects     # Offline-resilient score drift queue
```

**Dropped from original:**
- `pending_notifications` — push handled by Expo Push service directly
- `rate_limits` — handled by FastAPI middleware (`slowapi`)
- `claude_api_calls` — replaced by application-level logging

**Added:**
- `plan_cache` — maps `quiz_answer_hash` → `plan_json` to avoid duplicate LLM generation

### Key Schema (Unchanged Core)

The core schema from the existing `data-model.md` is preserved. The `users`, `progress`, `cycles`, `daily_tasks`, `plans`, `quiz_answers`, `achievements`, `challenge_progress`, `weekly_reports`, `micro_sprints`, `season_events`, `pending_task_effects`, and `task_library_selections` tables keep their current column definitions.

New table:

```sql
CREATE TABLE plan_cache (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quiz_hash       TEXT UNIQUE NOT NULL,
    plan_json       JSONB NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    hit_count       INTEGER DEFAULT 0
);
CREATE INDEX idx_plan_cache_hash ON plan_cache(quiz_hash);
```

### Migrations

Use **Alembic** for migration management:
```
src/database/
    migrations/
        versions/
            001_initial_schema.py
            002_plan_cache.py
            ...
    env.py
    alembic.ini
```

---

## 7. Deterministic Coaching Engine (No LLM)

The biggest cost saver. Replace all non-essential LLM coaching calls with a template engine.

### 7.1 Daily Insight Templates

~60 pre-written templates keyed by `(language_stage, context_type, direction)`:

```python
DAILY_INSIGHT_TEMPLATES = {
    ("outcome", "pillar_up", "skin"): [
        "Skin clarity improved {delta} points this cycle. UV protection and hydration are compounding.",
        "Your skin score moved to {score}. Consistent cleansing breaks down buildup over 21-day cycles.",
    ],
    ("outcome", "pillar_down", "grooming"): [
        "Grooming dipped {delta} points. Revisiting the evening routine anchors consistency.",
    ],
    ("habit", "streak_milestone", None): [
        "{streak}-day streak. The routine is becoming automatic — completion rate is {rate}%.",
    ],
    ("mechanism", "pillar_up", "skin"): [
        "Skin at {score}. Retinoid application accelerates epidermal turnover by binding RAR receptors.",
    ],
    # ... ~60 total templates
}
```

**Selection logic:**
1. Determine `stage` from `stageForDay(program_day)`
2. Find most relevant context: biggest pillar mover, streak milestone, completion rate
3. Pick template matching `(stage, context, pillar)`
4. Interpolate `{delta}`, `{score}`, `{streak}`, `{rate}`, `{pillar_name}`
5. Rotate templates to avoid repetition (track last-used index per user)

### 7.2 Weekly Report Templates

Structured markdown template filled with real data:

```markdown
## Week {week_number} Report — Day {start_day}–{end_day}

**Completion rate:** {completion_rate}% ({completed}/{total} tasks)

### Pillar Movement
{pillar_table}

### Coaching Note
{coaching_paragraph}

### Focus for Week {next_week}
{focus_paragraph}
```

- `pillar_table`: generated from DB query of pillar deltas for the week
- `coaching_paragraph`: selected from ~20 templates based on weakest pillar + stage
- `focus_paragraph`: selected from ~15 templates based on lowest pillar + upcoming tasks

### 7.3 Season Report Templates

Same approach — narrative template with data interpolation:

```markdown
## Season {season} Complete — 90 Days

{opening_paragraph}

### Before → After
{pillar_comparison_table}

### Biggest Mover: {biggest_mover_name}
{biggest_mover_paragraph}

### What Stuck
{habits_stuck_list}

### What Needs Work
{needs_work_list}

### Season {next_season} Focus
{next_focus_paragraph}
```

All paragraphs selected from template banks keyed by pillar and direction.

---

## 8. Security Model

| Concern | Solution |
|---|---|
| **LLM API keys** | Server-side only. Stored as env vars on Fly.io/Railway. Never in client code. |
| **Authentication** | JWT access tokens (15min expiry) + refresh tokens (7 days). `python-jose` for signing, `passlib[bcrypt]` for password hashing. |
| **Authorization** | Every endpoint validates `user_id` from JWT. DB queries always filter by `user_id`. |
| **Photo privacy** | Presigned upload URLs (5 min expiry) for R2. Presigned download URLs (1 hour expiry) for display. |
| **Rate limiting** | `slowapi` middleware. General: 60 req/min. LLM endpoints: plan generation 2/hr, photo analysis 5/hr. |
| **Input validation** | Pydantic v2 models on every request body and query param. |
| **CORS** | Strict allowlist: app domains only. No wildcard origins. |
| **SQL injection** | SQLAlchemy ORM with parameterized queries. No raw SQL from user input. |
| **Secrets management** | Env vars only (`DEEPSEEK_API_KEY`, `JWT_SECRET`, `R2_SECRET_KEY`, etc.). `.env` for local, platform secrets for prod. |
| **HTTPS** | Enforced by Fly.io/Railway. HSTS headers. |

---

## 9. Project Structure

```
forge-new/
├── PLANNING.md                      # This file
├── TASK.md                          # Task tracking
├── CHANGELOG.md                     # Change log
├── docs/                            # Feature specs, flows, data model (existing)
│
├── backend/                         # FastAPI backend
│   ├── pyproject.toml               # Dependencies (FastAPI, SQLAlchemy, Pydantic, etc.)
│   ├── requirements.txt             # Pinned dependencies
│   ├── alembic.ini                  # Alembic config
│   ├── docker-compose.yml           # Local PostgreSQL + backend
│   ├── Dockerfile                   # Production container
│   ├── .env.example                 # Env var template
│   │
│   ├── src/
│   │   ├── main.py                  # FastAPI app entry point
│   │   ├── config.py                # Settings via pydantic-settings
│   │   │
│   │   ├── auth/                    # Auth module
│   │   │   ├── router.py            # /signup, /login, /refresh, /delete
│   │   │   ├── service.py           # JWT creation, password hashing
│   │   │   ├── dependencies.py      # get_current_user dependency
│   │   │   ├── schemas.py           # Pydantic request/response models
│   │   │   └── tests/
│   │   │       └── test_auth.py
│   │   │
│   │   ├── users/                   # User profile
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── schemas.py
│   │   │   └── tests/
│   │   │
│   │   ├── quiz/                    # Quiz submission + score estimation
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── estimator.py         # Deterministic score estimator
│   │   │   ├── schemas.py
│   │   │   └── tests/
│   │   │
│   │   ├── plans/                   # Plan generation (DeepSeek V4-Flash)
│   │   │   ├── router.py
│   │   │   ├── service.py           # generate_plan(), uses plan_cache
│   │   │   ├── prompts.py           # System prompts for plan generation
│   │   │   ├── task_library.py      # ~150 curated tasks
│   │   │   ├── schemas.py
│   │   │   └── tests/
│   │   │
│   │   ├── tasks/                   # Daily task engine
│   │   │   ├── router.py
│   │   │   ├── service.py           # get_today, complete, heatmap
│   │   │   ├── schemas.py
│   │   │   └── tests/
│   │   │
│   │   ├── cycles/                  # Photo check-ins (DeepSeek VL2)
│   │   │   ├── router.py
│   │   │   ├── service.py           # upload, analyse, history
│   │   │   ├── photo_analyser.py    # DeepSeek VL2 integration
│   │   │   ├── prompts.py           # Vision analysis prompts
│   │   │   ├── schemas.py
│   │   │   └── tests/
│   │   │
│   │   ├── progress/                # Scores, streaks, XP
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── score_calculator.py  # Deterministic score engine
│   │   │   ├── schemas.py
│   │   │   └── tests/
│   │   │
│   │   ├── coaching/                # Deterministic coaching engine
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── templates.py         # ~60 daily insight templates
│   │   │   ├── weekly_templates.py  # ~20 weekly report templates
│   │   │   ├── season_templates.py  # Season report templates
│   │   │   ├── language_stage.py    # stage_for_day() logic
│   │   │   ├── schemas.py
│   │   │   └── tests/
│   │   │
│   │   ├── subscriptions/           # RevenueCat + Stripe webhooks
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── schemas.py
│   │   │   └── tests/
│   │   │
│   │   ├── gamification/            # Achievements, challenges, streak
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── badges.py            # Badge catalog
│   │   │   ├── challenges.py        # Challenge templates
│   │   │   ├── xp.py                # XP thresholds, level calc
│   │   │   ├── schemas.py
│   │   │   └── tests/
│   │   │
│   │   ├── share/                   # Share card generation
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   └── tests/
│   │   │
│   │   ├── notifications/           # Push notification service
│   │   │   ├── service.py           # Expo Push / FCM
│   │   │   └── tests/
│   │   │
│   │   ├── scheduler/               # Background jobs
│   │   │   ├── jobs.py              # Weekly report gen, season rollover, streak check
│   │   │   └── tests/
│   │   │
│   │   ├── database/                # DB layer
│   │   │   ├── connection.py        # SQLAlchemy async engine + session
│   │   │   ├── models.py            # SQLAlchemy ORM models (all 14 tables)
│   │   │   └── migrations/
│   │   │       └── versions/        # Alembic migration files
│   │   │
│   │   ├── storage/                 # Cloudflare R2 integration
│   │   │   ├── r2_client.py         # Presigned URL generation
│   │   │   └── tests/
│   │   │
│   │   └── common/                  # Shared utilities
│   │       ├── exceptions.py        # Custom exception classes
│   │       ├── middleware.py         # Rate limiter, request logging
│   │       └── constants.py         # Pillar names, phase names, etc.
│   │
│   └── tests/
│       ├── conftest.py              # Fixtures: test DB, test client
│       └── test_integration.py      # End-to-end API tests
│
├── mobile/                          # Expo React Native app (iOS + Android + Web)
│   ├── app/                         # Expo Router file-based routing
│   │   ├── _layout.tsx              # Root layout, auth guard
│   │   ├── (auth)/                  # Onboarding flow (no tabs)
│   │   └── (app)/                   # Main authenticated app (tabs)
│   ├── src/
│   │   ├── api/                     # API client (replaces direct Supabase calls)
│   │   │   ├── client.ts            # Axios/fetch wrapper with JWT interceptor
│   │   │   ├── auth.ts              # signup, login, refresh
│   │   │   ├── plans.ts             # generate, getCurrent
│   │   │   ├── tasks.ts             # getToday, complete, heatmap
│   │   │   ├── cycles.ts            # uploadUrl, analyse, history
│   │   │   ├── progress.ts          # getProgress, getPillar
│   │   │   ├── coaching.ts          # dailyInsight, weeklyReport, seasonReport
│   │   │   └── subscriptions.ts     # getStatus
│   │   ├── hooks/                   # React hooks (same as current, but call api/ instead of Supabase)
│   │   ├── components/              # UI components (preserved from current)
│   │   ├── store/                   # Zustand stores (preserved: user, program, progress)
│   │   ├── constants/               # Design tokens, task library, pillars, phases
│   │   └── types/                   # TypeScript types
│   ├── package.json
│   ├── tsconfig.json
│   └── app.config.ts
│
└── docs/                            # Existing documentation (preserved)
    ├── architecture.md              # Reference to old arch (kept for history)
    ├── data-model.md
    ├── design.md
    ├── features/
    ├── flows/
    └── ...
```

---

## 10. Cost Estimate

### Per User Per Season (90 Days)

| Item | Cost |
|---|---|
| DeepSeek V4-Flash — plan generation (1 call) | $0.005 |
| DeepSeek VL2 — photo analysis (30 calls) | $0.30 |
| **Total LLM per user/season** | **$0.31** |

### Monthly Infrastructure (at 1,000 users)

| Service | Cost |
|---|---|
| Fly.io (FastAPI server, 256MB shared-cpu) | $5/mo |
| Neon PostgreSQL (free tier, 0.5GB) | $0/mo |
| Cloudflare R2 (10GB storage, ~50k requests) | ~$1/mo |
| PostHog (free tier, 1M events) | $0/mo |
| Expo Push (free) | $0/mo |
| Domain + SSL (Cloudflare) | $0/mo |
| **Total infra** | **~$6/mo** |

### Monthly LLM (at 1,000 users)

| Call | Volume | Cost |
|---|---|---|
| Plan generation | ~333 (new seasons) | ~$1.67 |
| Photo analysis | ~10,000 | ~$100 |
| **Total LLM** | | **~$102/mo** |

### Grand Total at 1,000 Users

**~$108/mo** total operating cost vs ~$2,725/mo on the original architecture.

Revenue at 1,000 x $11/mo = $11,000/mo. Margin: **99%**.

---

## 11. Migration Path (Build Order)

| Phase | Deliverable | Depends On |
|---|---|---|
| **P1** | FastAPI scaffold + config + Docker Compose + local PostgreSQL | — |
| **P2** | Database models (SQLAlchemy) + Alembic migrations for all 14 tables | P1 |
| **P3** | Auth module (signup, login, JWT, refresh, delete account) | P1, P2 |
| **P4** | Quiz, Score Estimator, Task Library (deterministic endpoints) | P3 |
| **P5** | Plan generation endpoint (DeepSeek V4-Flash + plan cache) | P3, P4 |
| **P6** | Task engine (today's tasks, complete, XP, streak, drift) | P2, P3 |
| **P7** | Progress + Score calculator (deterministic) | P6 |
| **P8** | Coaching engine (deterministic templates — daily, weekly, season) | P7 |
| **P9** | Cloudflare R2 integration + presigned URLs | P1 |
| **P10** | Cycle check-ins + DeepSeek VL2 photo analysis | P9, P7 |
| **P11** | Gamification (achievements, challenges, streak milestones) | P6 |
| **P12** | Subscription webhooks (RevenueCat + Stripe) | P3 |
| **P13** | Background scheduler (weekly reports, season rollover) | P8 |
| **P14** | Expo frontend — API client layer replacing Supabase calls | P3–P13 |
| **P15** | React Native Web export + web deployment | P14 |
| **P16** | Production deployment (Fly.io + Neon + R2) | All |

---

## 12. Environment Variables

### Backend `.env`

```bash
# Database
DATABASE_URL=postgresql+asyncpg://forge:forge@localhost:5432/forge
DATABASE_URL_SYNC=postgresql://forge:forge@localhost:5432/forge  # for Alembic

# Auth
JWT_SECRET=<random-64-char-hex>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# DeepSeek
DEEPSEEK_API_KEY=<your-deepseek-api-key>
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-v4-flash
DEEPSEEK_VL_PROVIDER=replicate  # or "siliconflow" or "deepseek"
DEEPSEEK_VL_API_KEY=<vision-provider-api-key>

# Cloudflare R2
R2_ACCOUNT_ID=<cloudflare-account-id>
R2_ACCESS_KEY_ID=<r2-access-key>
R2_SECRET_ACCESS_KEY=<r2-secret-key>
R2_BUCKET_NAME=forge-photos
R2_PUBLIC_URL=https://photos.forge.app

# RevenueCat
REVENUECAT_WEBHOOK_SECRET=<webhook-auth-secret>

# Stripe (web)
STRIPE_SECRET_KEY=<stripe-secret>
STRIPE_WEBHOOK_SECRET=<stripe-webhook-secret>

# Push Notifications
EXPO_PUSH_ACCESS_TOKEN=<expo-push-token>

# PostHog
POSTHOG_API_KEY=<posthog-project-key>
POSTHOG_HOST=https://us.i.posthog.com

# App
APP_ENV=development  # or "production"
CORS_ORIGINS=http://localhost:8081,http://localhost:3000
```

### Mobile `.env`

```bash
EXPO_PUBLIC_API_URL=http://localhost:8000/api/v1    # dev
# EXPO_PUBLIC_API_URL=https://api.forge.app/api/v1  # prod
EXPO_PUBLIC_REVENUECAT_APPLE_KEY=appl_...
EXPO_PUBLIC_REVENUECAT_GOOGLE_KEY=goog_...
EXPO_PUBLIC_POSTHOG_KEY=phc_...
EXPO_PUBLIC_POSTHOG_HOST=https://us.i.posthog.com
EXPO_PUBLIC_APP_ENV=development
```

No LLM keys, no database credentials, no storage secrets on the client.

---

## 13. Open Decisions

| ID | Question | Impact | Default |
|---|---|---|---|
| OD-01 | DeepSeek VL2 provider: Replicate vs SiliconFlow vs self-host? | Cost + latency for photo analysis | Replicate (simplest) |
| OD-02 | Neon vs Supabase vs Railway for prod DB? | Free tier limits, scaling | Neon (best free tier) |
| OD-03 | Keep 5 native Swift modules or drop for cross-platform parity? | iOS-only features vs web support | Drop; use JS alternatives |
| OD-04 | Reduce cycle check-in frequency from 3 days to 5 days? | Saves ~40% VL2 costs | Keep 3 days (core UX) |
| OD-05 | Stripe for web payments or defer web monetisation? | Revenue from web users | Implement in P12 |
| OD-06 | Self-host PostHog or keep cloud free tier? | Data ownership vs maintenance | Cloud free tier |
