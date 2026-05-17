# FORGE — Data Model

> PostgreSQL schema reference. 17 migrations, 16 tables, full RLS.
> Schema source: `supabase/migrations/001–017`

---

## Key Design Decisions

### 1. Progress as a Single Row Per User

Each user has exactly one `progress` row (enforced by `UNIQUE(user_id)`). All nine pillar scores, streak counters, XP, and the optimisation score live in that single row. This is a deliberate trade-off: we sacrifice an append-only audit trail for simplicity and read performance. Every screen that displays any progress data — the home dashboard, the progress tab, the pillar drill-down — reads from one row. No aggregation queries, no window functions, no date-range scans. The trade-off is that we lose per-day score history; we accept this because the cycle check-in system (every 3 days) provides a coarser-grained historical record in the `cycles` table, which is sufficient for the before/after comparison feature and the photo timeline.

### 2. AI-Generated Content as JSONB

Three tables store AI-generated content as JSONB columns: `plans.raw_json` (the full 90-day plan from Claude), `cycles.ai_insight` (free-text coaching insight), and `weekly_reports.content` (structured report with pillar deltas and narrative). JSONB was chosen because the AI output schema is expected to evolve — new fields added to coaching reports, richer cycle analysis structures, plan metadata expansions. Storing these as JSONB means we can add fields without running migrations, and the database doesn't need to enforce a schema on data it treats as opaque. The application layer (TypeScript types with Zod validation in `src/types/ai.ts`) provides the actual schema enforcement at the boundary where AI responses enter the system.

### 3. Circular FK Resolution via Transactional Plan Saving

The dependency chain runs: `plans` → `daily_tasks` (FK to plans), `plans` → `task_library_selections` (FK to plans), and `daily_tasks` → `users`. The plan saving operation in `savePlanToDatabase()` runs as a single logical transaction: insert the plan row, insert all 90 days of daily tasks referencing that plan, insert task library selection records, and update the user's plan reference — all or nothing. If any insert fails, the entire operation rolls back. This means the plan cache (`src/lib/planCache.ts`) can safely assume that a plan ID in memory maps to a fully committed plan in the database with all its children intact.

### 4. Private Photo Bucket with Signed URLs

User photos are sensitive personal data. The original `user-photos` bucket was public (migration 002), which posed GDPR and privacy risks. Migration 010 migrated to a private `user-photos-private` bucket and locked down the original public bucket. Photos are now stored at `cycles/{user_id}/{filename}` and accessed exclusively through time-limited signed URLs (default 3600s expiry). This means: (a) a photo URL leaked from a client is useless after one hour, (b) bucket-level RLS still enforces that only the owning user can generate signed URLs for their own photos, and (c) the cycle history screen and photo timeline must use the signed URL service (`src/services/image/signedUrl.ts`) rather than direct bucket URLs.

### 5. Edge Function Tables Decoupled from Main Schema

The `pending_notifications` and `season_events` tables exist solely to serve the scheduled edge functions (`weekly-report-generator`, `streak-risk-notifier`, `season-rollover-handler`). They are kept in the same database but conceptually decoupled: no application screens query these tables directly, no application services write to them, and their failure modes are isolated. If a cron job fails to insert into `pending_notifications`, it does not affect the user's ability to complete tasks, check in, or view progress. This separation also means the notification queue can be rebuilt or migrated independently of the core application data.

### 6. Service Role Bypass on All Tables

Every table has a dual-policy RLS model (migration 008): a `service_role` policy that grants full access (`USING (true) WITH CHECK (true)`), and an `authenticated` policy that restricts to `auth.uid() = user_id`. Edge functions operate as `service_role` and need unrestricted access to query across users (e.g., the weekly report generator iterates all active users). The rate limits table (`rate_limits`) is an exception — only `service_role` can read or write it; authenticated users have no access at all. The `claude_api_calls` table is similarly locked to `service_role` only.

---

## Creation Order (FK-Safe Sequence)

Tables must be created in this order to satisfy foreign key dependencies:

| # | Table | Depends On |
|---|-------|-----------|
| 1 | `users` | — |
| 2 | `quiz_answers` | users |
| 3 | `plans` | users |
| 4 | `daily_tasks` | users, plans |
| 5 | `progress` | users |
| 6 | `cycles` | users |
| 7 | `achievements` | users |
| 8 | `challenge_progress` | users |
| 9 | `task_library_selections` | plans, users |
| 10 | `weekly_reports` | users |
| 11 | `micro_sprints` | users |
| 12 | `pending_notifications` | users |
| 13 | `season_events` | users |
| 14 | `claude_api_calls` | users |
| 15 | `pending_task_effects` | users |
| 16 | `rate_limits` | — (user_id nullable, no FK) |

---

## Full Schema

### Group 1 — Users & Auth

```sql
CREATE TABLE users (
  id                        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email                     TEXT UNIQUE NOT NULL,
  name                      TEXT,
  created_at                TIMESTAMPTZ DEFAULT NOW(),
  program_day               INTEGER DEFAULT 1,
  season                    INTEGER DEFAULT 1,
  onboarded                 BOOLEAN DEFAULT FALSE,
  plan_start_date           DATE,
  timezone                  TEXT DEFAULT 'UTC',
  baseline_photo_url        TEXT,
  baseline_photo_path       TEXT,
  face_shape                TEXT,
  referral_code             TEXT UNIQUE,
  referred_by               TEXT REFERENCES users(id) ON DELETE SET NULL,
  last_active_date          DATE,
  first_strike_completed    BOOLEAN DEFAULT false,
  subscription_tier         TEXT NOT NULL DEFAULT 'none',
  subscription_expires_at   TIMESTAMPTZ,
  subscription_provider     TEXT NOT NULL DEFAULT 'revenuecat',
  initial_compliment        TEXT,
  CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
  CHECK (name IS NULL OR LENGTH(name) BETWEEN 1 AND 100),
  CHECK (season >= 1 AND season <= 99)
);
```

**Comments:**
- `program_day`: Incremented daily (1–90 per season). Reset to 1 on season rollover.
- `season`: Current season number. Starts at 1, increments on each 90-day completion.
- `onboarded`: Set to `true` after plan-reveal saves plan to DB. Guards main app access.
- `baseline_photo_path`: Path in `user-photos-private` bucket (e.g. `cycles/{uuid}/baseline.jpg`).
- `face_shape`: Detected by Claude Vision on baseline photo. One of `oval`, `square`, `round`, `long`, `heart`, `diamond`. Adjusts pillar weights.
- `referral_code`: Auto-generated 6-char alphanumeric on insert (trigger `trg_generate_referral_code`).
- `referred_by`: Self-referential FK to `users.id`. `ON DELETE SET NULL` — deleting a user doesn't cascade-delete their referrals.
- `first_strike_completed`: Day 1 survival module completion flag. Controls whether the First Strike modal appears.
- `subscription_tier`: Synced by `revenuecat-webhook` edge function. Values: `none`, `basic`.
- `subscription_provider`: Always `revenuecat`. Reserved for future multi-provider support.
- `initial_compliment`: 15–25 word AI-generated strength callout from `compliPrompt.ts`, shown on plan reveal.

---

### Group 2 — Programs & Tasks

```sql
CREATE TABLE quiz_answers (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
  goals           TEXT[],
  routine_level   TEXT,
  daily_time      TEXT,
  timeline        TEXT,
  main_concern    TEXT,
  age_range       TEXT,
  has_photo       BOOLEAN DEFAULT FALSE,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE plans (
  id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id            UUID REFERENCES users(id) ON DELETE CASCADE,
  season             INTEGER DEFAULT 1,
  program_name       TEXT,
  focus_summary      TEXT,
  honest_expectation TEXT,
  raw_json           JSONB,
  created_at         TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE daily_tasks (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
  plan_id         UUID REFERENCES plans(id) ON DELETE CASCADE,
  title           TEXT NOT NULL,
  category        TEXT NOT NULL,
  why_it_works    TEXT,
  duration_mins   INTEGER,
  day_number      INTEGER NOT NULL,
  xp_value        INTEGER DEFAULT 10,
  is_completed    BOOLEAN DEFAULT FALSE,
  completed_at    TIMESTAMPTZ,
  library_task_id TEXT,
  pillar          TEXT NOT NULL DEFAULT 'skin',
  tier            TEXT NOT NULL DEFAULT 'beginner',
  week_number     INTEGER,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  CHECK (LENGTH(TRIM(title)) > 0),
  CHECK (xp_value >= 0),
  CHECK (day_number >= 1)
);

CREATE TABLE task_library_selections (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
  plan_id         UUID REFERENCES plans(id) ON DELETE CASCADE,
  library_task_id TEXT NOT NULL,
  used_count      INTEGER DEFAULT 1,
  season          INTEGER,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

**Comments:**
- `quiz_answers.goals`: Array of pillar or concern strings selected by user during quiz (e.g. `{skin, grooming, style}`).
- `plans.raw_json`: Full 90-day plan as JSONB. Structure defined in `src/types/plan.ts` (`GeneratedPlan`).
- `plans.focus_summary`: 2-sentence AI-generated summary of the plan's focus.
- `plans.honest_expectation`: AI-generated statement of what will and won't change in 90 days.
- `daily_tasks.pillar`: Must be one of the 9 pillars: `facial_composition`, `skin`, `grooming`, `hair`, `fitness` (posture), `style`, `sleep`, `nutrition`, `voice`.
- `daily_tasks.tier`: Task difficulty. Values: `beginner`, `intermediate`, `advanced`.
- `daily_tasks.week_number`: Computed as `CEIL(day_number / 7.0)`. Enables weekly filtering and reporting.
- `daily_tasks.library_task_id`: References a task ID from `src/constants/taskLibrary.ts`. Used for deduplication and selection tracking.
- `task_library_selections`: Tracks which library tasks were selected for a plan. `used_count` tracks reuse across seasons.

---

### Group 3 — Progress & Scoring

```sql
CREATE TABLE progress (
  id                        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id                   UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
  current_streak            INTEGER DEFAULT 0,
  longest_streak            INTEGER DEFAULT 0,
  last_active_date          DATE,
  total_xp                  INTEGER DEFAULT 0,
  level                     INTEGER DEFAULT 1,
  facial_composition_score  INTEGER DEFAULT 50,
  skin_score                INTEGER DEFAULT 50,
  grooming_score            INTEGER DEFAULT 50,
  hair_score                INTEGER DEFAULT 50,
  posture_score             INTEGER DEFAULT 50,
  style_score               INTEGER DEFAULT 50,
  sleep_score               INTEGER DEFAULT 50,
  nutrition_score           INTEGER DEFAULT 50,
  voice_score               INTEGER DEFAULT 50,
  optimisation_score        NUMERIC(5,2) DEFAULT 50.00,
  updated_at                TIMESTAMPTZ DEFAULT NOW(),
  -- 9-pillar score bounds
  CHECK (facial_composition_score BETWEEN 0 AND 100),
  CHECK (skin_score BETWEEN 0 AND 100),
  CHECK (grooming_score BETWEEN 0 AND 100),
  CHECK (hair_score BETWEEN 0 AND 100),
  CHECK (posture_score BETWEEN 0 AND 100),
  CHECK (style_score BETWEEN 0 AND 100),
  CHECK (sleep_score BETWEEN 0 AND 100),
  CHECK (nutrition_score BETWEEN 0 AND 100),
  CHECK (voice_score BETWEEN 0 AND 100),
  CHECK (optimisation_score BETWEEN 0 AND 100),
  -- Non-negative enforcement
  CHECK (current_streak >= 0),
  CHECK (longest_streak >= 0),
  CHECK (total_xp >= 0)
);
```

**Comments:**
- `UNIQUE(user_id)`: Enforces one progress row per user. Inserted during onboarding; never deleted.
- `posture_score`: Note that in the schema this is named `posture_score` in `progress` (the pillar is called `fitness` in the app but the DB column reflects the underlying trait — posture/frame).
- `optimisation_score`: Weighted composite of all 9 pillars. `NUMERIC(5,2)` allows scores like `73.45`.
- `last_active_date`: Updated when any task is completed. Used by streak calculation.
- All scores default to 50 (neutral baseline).

---

### Group 4 — Cycles

```sql
CREATE TABLE cycles (
  id                        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id                   UUID REFERENCES users(id) ON DELETE CASCADE,
  cycle_number              INTEGER NOT NULL,
  photo_url                 TEXT,
  photo_path                TEXT,
  cycle_type                TEXT DEFAULT 'regular',
  face_shape                TEXT,
  facial_composition_score  INTEGER,
  skin_score                INTEGER,
  grooming_score            INTEGER,
  hair_score                INTEGER,
  posture_score             INTEGER,
  style_score               INTEGER,
  sleep_score               INTEGER,
  nutrition_score           INTEGER,
  voice_score               INTEGER,
  ai_insight                TEXT,
  next_focus                TEXT,
  checked_in_at             TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, cycle_number),
  CHECK (facial_composition_score IS NULL OR facial_composition_score BETWEEN 0 AND 100),
  CHECK (skin_score IS NULL OR skin_score BETWEEN 0 AND 100),
  CHECK (grooming_score IS NULL OR grooming_score BETWEEN 0 AND 100),
  CHECK (hair_score IS NULL OR hair_score BETWEEN 0 AND 100),
  CHECK (posture_score IS NULL OR posture_score BETWEEN 0 AND 100),
  CHECK (style_score IS NULL OR style_score BETWEEN 0 AND 100),
  CHECK (sleep_score IS NULL OR sleep_score BETWEEN 0 AND 100),
  CHECK (nutrition_score IS NULL OR nutrition_score BETWEEN 0 AND 100),
  CHECK (voice_score IS NULL OR voice_score BETWEEN 0 AND 100)
);
```

**Comments:**
- `cycle_number`: Auto-assigned by trigger `trg_assign_cycle_number` (BEFORE INSERT). Computed as `MAX(cycle_number) + 1` for the user.
- `UNIQUE(user_id, cycle_number)`: Prevents duplicate cycle numbers from concurrent inserts.
- `cycle_type`: Values: `regular` (every-3-day check-in), can also be extended for `baseline` and `season_end`.
- `photo_path`: Path in private bucket. Used to generate signed URLs for rendering.
- `ai_insight`: Free-text coaching insight from Claude Vision analysis.
- `next_focus`: Single pillar name — the highest-leverage area to focus on for the next 3 days.

---

### Group 5 — Gamification

```sql
CREATE TABLE achievements (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID REFERENCES users(id) ON DELETE CASCADE,
  badge_id      TEXT NOT NULL,
  unlocked_at   TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, badge_id)
);

CREATE TABLE challenge_progress (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id        UUID REFERENCES users(id) ON DELETE CASCADE,
  challenge_id   TEXT NOT NULL,
  status         TEXT DEFAULT 'active',
  progress       INTEGER DEFAULT 0,
  target         INTEGER NOT NULL,
  started_at     TIMESTAMPTZ DEFAULT NOW(),
  completed_at   TIMESTAMPTZ,
  CHECK (target > 0),
  CHECK (progress >= 0)
);
```

**Comments:**
- `achievements.badge_id`: References a badge from `src/constants/badges.ts`. `UNIQUE(user_id, badge_id)` prevents duplicate awards.
- `challenge_progress.status`: Values: `active`, `completed`, `expired`.
- `challenge_progress.target`: The numeric goal (e.g., complete 7 tasks, reach streak of 14).
- `challenge_progress.progress`: Current count toward the target. Incremented by `challengeEngine.onTaskComplete()`.

---

### Group 6 — Coaching

```sql
CREATE TABLE weekly_reports (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID REFERENCES users(id) ON DELETE CASCADE,
  week_number   INTEGER NOT NULL,
  generated_at  TIMESTAMPTZ DEFAULT NOW(),
  content       JSONB NOT NULL
);

CREATE TABLE micro_sprints (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id        UUID REFERENCES users(id) ON DELETE CASCADE,
  sprint_type    TEXT NOT NULL,
  started_at     TIMESTAMPTZ DEFAULT NOW(),
  ended_at       TIMESTAMPTZ,
  tasks          JSONB NOT NULL
);
```

**Comments:**
- `weekly_reports.content`: JSONB with structure: `{ summary, pillar_deltas, focus_next_week, narrative }`.
- `weekly_reports.week_number`: 1–13 (90 days ≈ 13 weeks per season).
- `micro_sprints.sprint_type`: Event-driven sprint types from `src/constants/microSprints.ts` (e.g. `wedding`, `interview`, `date_night`).
- `micro_sprints.tasks`: JSONB array of sprint-specific tasks overriding the normal daily plan.

---

### Group 7 — System

```sql
CREATE TABLE pending_notifications (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
  type            TEXT NOT NULL,
  scheduled_for   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  sent_at         TIMESTAMPTZ,
  payload         JSONB,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE season_events (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
  event_type      TEXT NOT NULL,
  from_season     INTEGER NOT NULL,
  to_season       INTEGER,
  event_data      JSONB,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE claude_api_calls (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
  model           TEXT NOT NULL,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE pending_task_effects (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
  task_id         UUID NOT NULL,
  pillar          TEXT NOT NULL,
  drift           NUMERIC(5,2) NOT NULL DEFAULT 0.5,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  applied_at      TIMESTAMPTZ
);

CREATE TABLE rate_limits (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID,
  fingerprint     TEXT,
  action          TEXT NOT NULL,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

**Comments:**
- `pending_notifications.type`: Values: `streak_risk`, `cycle_prompt`, `weekly_report`, `day_1_welcome`. Edge functions insert, client polls.
- `pending_notifications.scheduled_for`: The intended delivery time. Indexed for efficient polling queries.
- `pending_notifications.sent_at`: NULL until the notification is delivered. Used for idempotency.
- `season_events.event_type`: Values: `season_rollover`, `season_activated`, `season_completed`. Audit-only table.
- `season_events.from_season` / `to_season`: Tracks season transitions (e.g. 1 → 2).
- `claude_api_calls`: Insert-only table for tracking API usage per user. Used by the `claude-proxy` edge function for rate limiting (20 req/hour/user).
- `pending_task_effects.drift`: Default +0.5 points applied to the task's pillar score. Inserted when `applyTaskEffect()` fails due to network; retried on next app boot.
- `pending_task_effects.applied_at`: NULL until the effect is successfully applied, then set to the application timestamp.
- `rate_limits.fingerprint`: Anonymous rate-limit key (e.g., IP hash) for unauthenticated requests.
- `rate_limits`: Auto-cleanup cron deletes entries older than 1 hour every 5 minutes.

---

## Indexes

| Index Name | Table | Columns | Query Pattern Purpose |
|---|---|---|---|
| `idx_daily_tasks_user_day` | `daily_tasks` | `(user_id, day_number)` | `getTodaysTasks` query — fetch all tasks for a user on a specific day |
| `idx_daily_tasks_week_pillar` | `daily_tasks` | `(user_id, week_number, pillar)` | Weekly reports and pillar filtering — aggregate tasks by week and pillar |
| `idx_cycles_type` | `cycles` | `(user_id, cycle_type)` | Filter check-ins by type (regular vs baseline vs season_end) |
| `idx_pending_notifications_user_scheduled` | `pending_notifications` | `(user_id, scheduled_for)` | Edge function queries — find pending notifications by user and time |
| `idx_pending_notifications_user_type_scheduled` | `pending_notifications` | `(user_id, type, scheduled_for)` | Idempotency checks — prevent duplicate notifications for same user+type+time |
| `idx_season_events_user_created` | `season_events` | `(user_id, created_at DESC)` | Audit log queries — view season event history in reverse chronological order |
| `idx_claude_api_calls_user_created` | `claude_api_calls` | `(user_id, created_at DESC)` | Rate limit checks — count API calls in the last hour per user |
| `idx_users_referral_code` | `users` | `(referral_code)` | Referral lookup — find user by their 6-char referral code |
| `idx_users_program_day` | `users` | `(id, program_day)` | Program advancement — query users by current program day for rollover detection |
| `idx_users_season` | `users` | `(id, season)` | Season queries — filter users by current season |
| `cycles_user_cyclenum_unique` | `cycles` | `(user_id, cycle_number)` UNIQUE | Prevents duplicate cycle numbers from concurrent inserts |

---

## Entity Relationship Summary

```
                              ┌──────────────────┐
                              │      users       │
                              │ (PK) id          │◄──────────────────────┐
                              │     email        │                       │
                              │     referral_code│──┐  (referred_by)     │
                              │     referred_by  │◄─┘  self-ref FK      │
                              └────────┬─────────┘                       │
                                       │                                 │
         ┌─────────────────────────────┼─────────────────────────────┐   │
         │                             │                             │   │
         ▼                             ▼                             ▼   │
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐     │
│   quiz_answers   │    │      plans       │    │    progress      │     │
│ (PK) id          │    │ (PK) id          │    │ (PK) id          │     │
│ (FK) user_id ────┘    │ (FK) user_id ────┘    │ (FK) user_id ────┘     │
└──────────────────┘    └────────┬─────────┘    └──────────────────┘     │
                                 │           UNIQUE(user_id)             │
                                 │                                       │
                    ┌────────────┼────────────┐                          │
                    │            │            │                          │
                    ▼            ▼            ▼                          │
           ┌────────────┐ ┌────────────┐ ┌──────────────────────┐       │
           │daily_tasks │ │task_lib_   │ │     achievements     │       │
           │(PK) id     │ │selections  │ │ (PK) id              │       │
           │(FK) user_id│ │(PK) id     │ │ (FK) user_id ────────┘       │
           │(FK) plan_id│ │(FK) user_id│ └──────────────────────┘       │
           └────────────┘ │(FK) plan_id│                                 │
                          └────────────┘                                 │
                                                                         │
         ┌───────────────────────────────────────────────────────────────┤
         │                │                │                │            │
         ▼                ▼                ▼                ▼            │
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐     │
│    cycles    │ │  challenge_  │ │   weekly_    │ │   micro_     │     │
│ (PK) id      │ │   progress   │ │   reports    │ │   sprints    │     │
│ (FK) user_id─┤ │ (PK) id      │ │ (PK) id      │ │ (PK) id      │     │
│ cycle_number │ │ (FK) user_id─┤ │ (FK) user_id─┤ │ (FK) user_id─┘     │
│ UNIQUE(uid,c)│ │ challenge_id │ │ week_number  │ │ sprint_type        │
└──────────────┘ │ status       │ │ content(JSON)│ │ tasks(JSON)        │
                 └──────────────┘ └──────────────┘ └──────────────┘     │
                                                                         │
         ┌───────────────────────────────────────────────────────────────┤
         │                │                │                │            │
         ▼                ▼                ▼                ▼            │
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐     │
│   pending_   │ │   season_    │ │   claude_    │ │   pending_   │     │
│ notifications│ │   events     │ │  api_calls   │ │ task_effects │     │
│ (PK) id      │ │ (PK) id      │ │ (PK) id      │ │ (PK) id      │     │
│ (FK) user_id─┤ │ (FK) user_id─┤ │ (FK) user_id─┤ │ (FK) user_id─┘     │
│ type         │ │ event_type   │ │ model        │ │ pillar            │
│ scheduled_for│ │ from/to_seas │ │ created_at   │ │ drift             │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘     │
                                                                         │
                                              ┌──────────────┐          │
                                              │  rate_limits │          │
                                              │ (PK) id      │          │
                                              │ user_id (?)  │──────────┘
                                              │ fingerprint  │  (nullable,
                                              │ action       │   no FK)
                                              └──────────────┘
```

**Relationship summary** (all `ON DELETE CASCADE` unless noted):
- `users` 1──* `quiz_answers`
- `users` 1──* `plans`
- `users` 1──* `daily_tasks`
- `plans` 1──* `daily_tasks`
- `users` 1──1 `progress` (UNIQUE)
- `users` 1──* `cycles`
- `users` 1──* `achievements`
- `users` 1──* `challenge_progress`
- `plans` 1──* `task_library_selections`, `users` 1──* `task_library_selections`
- `users` 1──* `weekly_reports`
- `users` 1──* `micro_sprints`
- `users` 1──* `pending_notifications`
- `users` 1──* `season_events`
- `users` 1──* `claude_api_calls`
- `users` 1──* `pending_task_effects`
- `users` 1──* `rate_limits` (nullable, no FK constraint)
- `users` 1──* `users` (self-ref via `referred_by`, ON DELETE SET NULL)

---

## RLS Policies (Migration 008)

Every table has two policies:

```sql
-- Pattern for tables with a user_id column:
CREATE POLICY "{table}_service_role" ON {table}
  FOR ALL TO service_role
  USING (true)
  WITH CHECK (true);

CREATE POLICY "{table}_own_data" ON {table}
  FOR ALL TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);
```

**Special cases:**
- `task_library_selections`: Uses a subquery join through `plans` — `auth.uid() IN (SELECT user_id FROM plans WHERE plans.id = task_library_selections.plan_id)`. A simpler `auth.uid() = user_id` policy was added in migration 016 after the `user_id` column was added.
- `claude_api_calls`: `service_role` only. Authenticated users cannot read or write.
- `rate_limits`: `service_role` only. Authenticated users cannot read or write.

---

## Triggers

| Trigger | Table | Event | Function | Purpose |
|---|---|---|---|---|
| `trg_users_referral_code` | `users` | BEFORE INSERT | `trg_generate_referral_code()` | Auto-generate unique 6-char referral code if null |
| `trg_cycles_assign_number` | `cycles` | BEFORE INSERT | `trg_assign_cycle_number()` | Auto-assign `cycle_number = MAX + 1` per user |

---

## Common Query Patterns

### 1. Resume Dashboard (get user progress + today's tasks)

```sql
-- User's progress row (single row, always exists)
SELECT *
FROM progress
WHERE user_id = $1;

-- Today's tasks for program_day = 14
SELECT dt.*
FROM daily_tasks dt
WHERE dt.user_id = $1
  AND dt.day_number = $2
ORDER BY dt.created_at;

-- Combined: single round-trip via CTE
WITH user_progress AS (
  SELECT * FROM progress WHERE user_id = $1
),
todays_tasks AS (
  SELECT * FROM daily_tasks
  WHERE user_id = $1 AND day_number = $2
)
SELECT
  (SELECT row_to_json(user_progress) FROM user_progress) AS progress,
  (SELECT json_agg(row_to_json(todays_tasks)) FROM todays_tasks) AS tasks;
```

### 2. Heatmap Data (all task completions for 90-day grid)

```sql
SELECT day_number, COUNT(*) AS completed_count
FROM daily_tasks
WHERE user_id = $1
  AND is_completed = TRUE
  AND day_number BETWEEN 1 AND 90
GROUP BY day_number
ORDER BY day_number;
```

### 3. Cycle History (all cycles with scores, ordered)

```sql
SELECT
  cycle_number,
  cycle_type,
  photo_url,
  facial_composition_score,
  skin_score,
  grooming_score,
  hair_score,
  posture_score,
  style_score,
  sleep_score,
  nutrition_score,
  voice_score,
  ai_insight,
  next_focus,
  checked_in_at
FROM cycles
WHERE user_id = $1
ORDER BY cycle_number DESC;
```

### 4. Active Challenge (latest active challenge with progress)

```sql
SELECT *
FROM challenge_progress
WHERE user_id = $1
  AND status = 'active'
ORDER BY started_at DESC
LIMIT 1;
```

### 5. Weekly Report (latest report for a user)

```sql
SELECT *
FROM weekly_reports
WHERE user_id = $1
ORDER BY week_number DESC
LIMIT 1;
```

### 6. Season Rollover Detection (users at day 90, season 1)

```sql
SELECT id, program_day, season, plan_start_date
FROM users
WHERE program_day >= 90
  AND season = 1
  AND onboarded = TRUE;
```

---

## Migration History

| # | File | Summary |
|---|------|---------|
| 001 | `001_initial_schema.sql` | Core tables: users, quiz_answers, plans, daily_tasks, progress, cycles, achievements, challenge_progress. Initial RLS. |
| 002 | `002_storage_setup.sql` | Public `user-photos` bucket, storage RLS policies. |
| 003 | `003_nine_pillar_migration.sql` | Extend progress/cycles to 9 pillars, add task_library_selections, weekly_reports, micro_sprints, daily_tasks columns (pillar, tier, week_number, library_task_id). |
| 004 | `004_plan_start_date.sql` | Add `users.plan_start_date`. |
| 005 | `005_timezone_field.sql` | Add `users.timezone`, default `'UTC'`. |
| 006 | `006_edge_function_tables.sql` | Create `pending_notifications` and `season_events`. |
| 007 | `007_schedule_edge_functions.sql` | Schedule 3 edge functions via `pg_cron` + `pg_net`. |
| 008 | `008_security_hardening.sql` | CHECK constraints on all tables, dual-policy RLS (service_role + authenticated), `rate_limits` table, `verify_cron_secret()` function, cron job hardening. |
| 009 | `009_claude_api_calls.sql` | Create `claude_api_calls` for rate limit tracking. |
| 010 | `010_private_photo_bucket.sql` | Private bucket `user-photos-private`, signed URLs, `photo_path` columns on cycles and users, lock down public bucket. |
| 011 | `011_referral_codes.sql` | Add `referral_code` + `referred_by` columns, auto-generation trigger, index. |
| 012 | `012_program_day_advancement.sql` | Add `users.last_active_date`, indexes for program_day and season. |
| 013 | `013_first_strike.sql` | Add `users.first_strike_completed` boolean. |
| 014 | `014_subscription_columns.sql` | Add `subscription_tier`, `subscription_expires_at`, `subscription_provider` to users. |
| 015 | `015_cycle_number_auto_assign.sql` | BEFORE INSERT trigger for auto-assigning cycle_number, UNIQUE constraint on (user_id, cycle_number). |
| 016 | `016_task_library_selections_user_id.sql` | Add `user_id` column to task_library_selections, simplified RLS policies. |
| 017 | `017_pending_task_effects.sql` | Create `pending_task_effects` for offline-resilient score drift. |

---

## Storage Buckets

| Bucket | Public | Purpose | Access Pattern |
|---|---|---|---|
| `user-photos` | false (was true) | Legacy bucket, now locked down | Migrated to private in migration 010 |
| `user-photos-private` | false | Current photo storage | Signed URLs via `src/services/image/signedUrl.ts`, 3600s expiry |

Object path convention: `cycles/{user_id}/{filename}`.
