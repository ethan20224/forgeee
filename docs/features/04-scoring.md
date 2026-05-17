# Feature: Scoring System

**Actor:** System, User (Member)
**Phase:** MVP ✅ Done
**Related flows:** [daily-routine-flow.md](../flows/daily-routine-flow.md), [cycle-checkin-flow.md](../flows/cycle-checkin-flow.md)
**Implementation:** `src/services/scores/scoreCalculator.ts`, `src/services/scores/quizScoreEstimator.ts`, `src/constants/faceShapeWeights.ts`, `src/constants/pillars.ts`, `src/hooks/useProgress.ts`

## Purpose

Measure and track the user's appearance improvement across 9 pillars using a weighted composite score (FORGE Optimisation Score 0-100). Scores change through cycle check-ins (Claude Vision ground truth), task completions (incremental +0.5 drift), and season rollovers (weight recalibration). The score is the single source of truth for all coaching, gamification, and progress display.

## Core Types

```typescript
type Pillar = "facial_composition" | "skin" | "grooming" | "hair"
            | "posture" | "style" | "sleep" | "nutrition" | "voice"

type PillarScore = { score: number | null; delta: number | null; confidence: "high" | "medium" | "low" | "data_gap" | null }
type PillarScores = Record<Pillar, PillarScore>
type PillarWeights = Record<Pillar, number> // must sum to 1.0

type OptimisationScore = {
  current: number    // weighted composite, 0-100
  baseline: number   // always 50 (neutral starting point)
  delta: number      // current - baseline
}
```

---

## Subsections

### 4.1 9-Pillar Model

The 9 pillars represent every dimension of male appearance that FORGE measures and improves:

| # | Pillar Key | Display Name | What It Measures | Primary Data Source |
|---|-----------|-------------|------------------|-------------------|
| 1 | `facial_composition` | Facial Structure | Jawline definition, symmetry, facial fat distribution | Cycle photo (Claude Vision) |
| 2 | `skin` | Skin | Clarity, tone evenness, texture, hydration | Cycle photo + task completion drift |
| 3 | `grooming` | Grooming | Eyebrow shape, facial hair neatness, nail care | Cycle photo + task completion drift |
| 4 | `hair` | Hair | Style suitability, scalp health, hairline framing | Cycle photo (Claude Vision) |
| 5 | `posture` | Posture | Neck alignment, shoulder position, spinal curvature | Cycle photo (full mode) |
| 6 | `style` | Style | Clothing fit, colour coordination, outfit cohesion | Cycle photo (full mode) + task completion drift |
| 7 | `sleep` | Sleep | Under-eye appearance, skin recovery markers | Self-reported task completion |
| 8 | `nutrition` | Nutrition | Skin inflammation, water retention, facial puffiness | Self-reported task completion |
| 9 | `voice` | Voice | Tone, clarity, projection (Season 2+) | Task completion rate proxy |

**Visibility Rules:**
- `VISIBLE_PILLARS` constant in `src/constants/pillars.ts` controls which pillars display in UI by default.
- Voice pillar is hidden in Season 1 (unlocked in Season 2 via `applySeasonalReweight`).
- `data_gap` confidence pillars (assessed by Claude but limited by photo angle) shown muted.
- `null` confidence pillars (not assessed at all) hidden from most views.

**Default Values:**
- New users: all pillars default to 50 (neutral baseline).
- No progress row yet (first task completion): pillar scores default to 50 before drift applies.
- Progress row created on first score-affecting event (task completion, cycle check-in).

**Acceptance Criteria:**
- AC-1.1: All 9 pillars defined with correct keys and display names.
- AC-1.2: `PILLAR_DISPLAY` maps all keys to user-facing names.
- AC-1.3: `VISIBLE_PILLARS` excludes voice in Season 1.
- AC-1.4: Default score is 50 for new users.
- AC-1.5: `pillarDisplayName(key)` returns correct display name.
- AC-1.6: Confidence levels map correctly to UI treatment (muted/hidden).

---

### 4.2 FORGE Optimisation Score

**Implementation:** `scoreCalculator.calculateOptimisationScore(pillars, weights)`

**Formula:**
```
optimisationScore = Σ(pillar_i.score × weight_i) for i in 1..9
```
Where `weight_i` is the user's personalised pillar weight (from quiz + face shape), and scores come from the latest cycle check-in.

**Weight Derivation** (`deriveInitialWeights`):
1. **Base weights:** Equal distribution — each pillar gets `1/9 ≈ 0.111`.
2. **Quiz concern boost:** If `mainConcern` is set (from quiz), boost the concern's pillar(s) by +0.05.
   - `skin` concern → `skin: +0.05`
   - `grooming` concern → `grooming: +0.05`
   - `hair` concern → `hair: +0.05`
   - `posture` concern → `posture: +0.05, style: +0.05`
   - `style` concern → `style: +0.05, posture: +0.05`
3. **Face shape adjustment:** If face shape detected (from baseline photo), apply deltas from `FACE_SHAPE_WEIGHTS` constant (see subsection 4.5).
4. **Normalisation:** After all adjustments, re-normalise all weights so they sum to exactly 1.0: `weight_i / totalWeight`.

**Seasonal Reweight** (`applySeasonalReweight`):
- Season 1: voice has weight 0 (excluded from score).
- Season 2+: voice is added with weight 0.11. Other weights reduced proportionally to maintain sum = 1.0.

**Score Calculation Edge Cases:**
- If a pillar score is `null` (not yet assessed): that pillar contributes 0 to the sum rather than skewing the average. The formula effectively skips null pillars: `sum(scores[i] * weights[i]) / sum(weights_for_non_null_pillars)`.
- If ALL pillars are null: optimisation score defaults to 50 (baseline).
- Baseline is always 50 — deltas are always relative to this fixed point.

**Acceptance Criteria:**
- AC-2.1: Optimisation score computed as weighted average of 9 pillar scores.
- AC-2.2: Weights always sum to exactly 1.0 after derivation.
- AC-2.3: Quiz concern boosts correct pillars by +0.05.
- AC-2.4: Face shape adjusts weights via `FACE_SHAPE_WEIGHTS`.
- AC-2.5: Null pillars excluded from calculation (don't skew average).
- AC-2.6: All-null pillars returns 50 (baseline).
- AC-2.7: Voice excluded in Season 1, included from Season 2.
- AC-2.8: Delta always computed as `current - 50`.

---

### 4.3 Quiz Score Estimator

**Implementation:** `quizScoreEstimator.estimateScoreFromQuiz(answers)`

Pre-signup score prediction that serves as a psychological hook. Estimates what the user's FORGE Score might be right now based on quiz answers alone — before any photo analysis.

**Estimation Logic:**
1. **Base:** All 9 pillars start at 50.
2. **Routine Level Adjustment:**
   - `none` → -10 to skin, grooming, hair/2
   - `basic` → -3 to same pillars
   - `moderate` → +2
   - `advanced` → +6
3. **Main Concern Penalty:** The user's biggest concern gets penalised (-5 to -10):
   - `skin` → skin: -10, grooming: -5
   - `hair` → hair: -10, facial_composition: -3
   - `grooming` → grooming: -10, skin: -3
   - `posture` → posture: -10, style: -3
   - `style` → style: -10, grooming: -3
4. **Daily Time Bonus:** More time = higher potential:
   - `5min` → -3
   - `15min` → 0
   - `30min` → +3
   - `1hr` → +5
5. **Timeline Bonus:** Longer commitment = better outcome expectation:
   - `30days` → 0
   - `90days` → +2
   - `6months` → +4
   - `1year` → +6
6. **Goal Adjustments:** Specific goals modify pillars (both positive and negative):
   - `skin` goal → skin: -3 (user knows it's a weakness)
   - `grooming` goal → grooming: -3
   - `fitness` goal → posture: +3, nutrition: +3
   - `style` goal → style: -3
   - `all` goal → skin: +2, grooming: +2, style: +2
7. **Clamp:** All individual pillar estimates clamped to 20-80 range.
8. **Composite:** Weighted average using fixed estimator weights (facial_composition: 0.18, skin: 0.15, grooming: 0.14, hair: 0.12, posture: 0.11, style: 0.10, sleep: 0.08, nutrition: 0.07, voice: 0.05).

**Output:** `{ estimated: number, rangeLow: number, rangeHigh: number, pillarEstimates: Record<string, number> }`
- `rangeLow = max(20, estimated - 3)`
- `rangeHigh = min(85, estimated + 3)`

**Display:** Shown on `estimated-score` screen before signup. Never persisted to database — purely UI.

**Acceptance Criteria:**
- AC-3.1: Estimator returns score within 20-85 range.
- AC-3.2: All quiz answer fields map to score adjustments.
- AC-3.3: Concern penalties are negative (user's weakness).
- AC-3.4: Routine level and time commitment are positive modifiers.
- AC-3.5: Range low and high are ±3 from estimated (clamped).
- AC-3.6: Estimator result never saved to database.
- AC-3.7: Fixed weights used for estimation (not user's actual weights).

---

### 4.4 Task Effect Drift

**Implementation:** `scoreCalculator.applyTaskEffect(userId, pillar)`

Incremental score improvement from daily task completion. Each completed task adds +0.5 to its pillar's score, representing compounding improvement from consistent habit execution.

**Drift Mechanics:**
- **Amount:** Fixed +0.5 per task completion. Not configurable — constant in code.
- **Cap:** Pillar scores capped at 100. Drift beyond 100 is discarded (no overflow).
- **Floor:** No floor — scores can theoretically go to 0 via negative deltas from cycle check-ins, but drift is always positive.
- **Weight Recalculation:** After applying drift, the optimisation score is recalculated using the user's current pillar weights (from quiz + face shape). Weights are re-fetched from the database to ensure accuracy.

**Pipeline:**
1. Map `pillar` key to progress table column name (e.g., `skin` → `skin_score`).
2. Fetch current progress row to get existing score.
3. Compute `newScore = min(currentScore + 0.5, 100)`.
4. Fetch user's face shape and quiz answers to derive current weights.
5. Recalculate optimisation score with updated weights and scores.
6. Upsert progress row with new pillar score and new optimisation score.

**Pending Effects Queue** (`pending_task_effects` table):
- Before calling `applyTaskEffect`, the task engine inserts a pending row: `{ user_id, task_id, pillar, drift: 0.5 }`.
- If `applyTaskEffect` succeeds: mark row `applied_at = NOW()`.
- If `applyTaskEffect` fails (network): row stays unapplied. On next app launch, `retryPendingEffects(userId)` picks up unapplied rows and retries.

**Race Condition Protection:**
- `applyTaskEffect` is called for each task independently.
- Two tasks for the same pillar completing simultaneously: both read current score, both write `current + 0.5`. This could lose one drift.
- Mitigation: task completion is sequential (one task at a time in UI), so concurrent writes to the same pillar are unlikely in practice.
- For extra safety: `retryPendingEffects` replays any missed drifts on app boot.

**Acceptance Criteria:**
- AC-4.1: Each task completion adds +0.5 to task's pillar score.
- AC-4.2: Score capped at 100 (no overflow beyond cap).
- AC-4.3: Optimisation score recalculated after drift.
- AC-4.4: Pending effect row created before applying drift.
- AC-4.5: Successful drift marks pending effect as applied.
- AC-4.6: Failed drift retried on next app launch.
- AC-4.7: Drift applies to correct pillar column in progress table.
- AC-4.8: Weight recalculation uses current user weights.

---

### 4.5 Face Shape Weights

**Implementation:** `src/constants/faceShapeWeights.ts` → `FACE_SHAPE_WEIGHTS`

Face shape detected by Claude Vision during baseline photo analysis adjusts pillar weights to personalise the FORGE Score to the user's facial structure. Different face shapes benefit from emphasis on different pillars.

**Detection:** Face shape detected during baseline photo analysis. Stored on `users.face_shape`. Re-detection on subsequent cycles is not currently performed (OQ-02: deferred decision).

**Weight Deltas by Face Shape:**

| Face Shape | Facial Comp. | Skin | Grooming | Hair | Posture | Style | Sleep | Nutrition | Voice |
|-----------|-------------|------|----------|------|---------|-------|-------|-----------|-------|
| **Oval** (balanced) | 0.15 | 0.12 | 0.12 | 0.12 | 0.10 | 0.12 | 0.12 | 0.12 | 0.03 |
| **Square** (strong jaw) | 0.12 | 0.15 | 0.10 | 0.10 | 0.10 | 0.15 | 0.12 | 0.12 | 0.04 |
| **Round** (soft angles) | 0.12 | 0.12 | 0.15 | 0.15 | 0.10 | 0.12 | 0.12 | 0.12 | 0.00 |
| **Long** (vertical emphasis) | 0.14 | 0.12 | 0.10 | 0.10 | 0.15 | 0.12 | 0.12 | 0.12 | 0.03 |
| **Heart** (wider forehead) | 0.12 | 0.15 | 0.14 | 0.12 | 0.10 | 0.12 | 0.12 | 0.12 | 0.02 |
| **Diamond** (narrow forehead) | 0.12 | 0.12 | 0.12 | 0.12 | 0.12 | 0.12 | 0.12 | 0.12 | 0.02 |

**Application:**
- These values are fed directly into `deriveInitialWeights` when face shape is detected.
- Each face shape's weights sum to 1.0 already — no re-normalisation needed for the face shape step alone, but the combined quiz concern + face shape weights are re-normalised together.
- Face shape weights override the equal base distribution (0.111 each).

**Rationale:**
- **Oval:** Naturally balanced — slight emphasis on facial composition, everything else equal.
- **Square:** Strong structure — emphasise skin and style to complement the jaw.
- **Round:** Softer angles — emphasise grooming and hair to create definition.
- **Long:** Vertical elongation — emphasise posture to balance proportions.
- **Heart:** Wider top — emphasise skin and grooming to draw attention to centre.
- **Diamond:** Angular — equal distribution, minor voice emphasis.

**Acceptance Criteria:**
- AC-5.1: All 6 face shapes have defined weight deltas.
- AC-5.2: Face shape detected from baseline photo analysis.
- AC-5.3: Weights applied via `deriveInitialWeights` when face shape present.
- AC-5.4: Combined quiz + face shape weights re-normalised to sum 1.0.
- AC-5.5: Face shape stored on `users.face_shape` after detection.
- AC-5.6: No face shape → equal weights used (fallback).

---

### 4.6 Score Clamping

**Implementation:** `scoreCalculator` — inline clamping in `applyTaskEffect`, `photoAnalyser.clampAnalysis()`

All scores in the system are clamped to the range [0, 100] to prevent meaningless or misleading values. Negative deltas (from cycle check-in comparisons) are allowed up to -100.

**Clamping Rules:**
- **Pillar scores:** Clamped to [0, 100]. Cannot go below 0 (no negative appearance scores).
- **Optimisation score:** Clamped to [0, 100] by nature of weighted average of 0-100 scores.
- **Pillar deltas:** Clamped to [-100, 100]. Negative deltas allowed (score can go down between cycles).
- **Score estimator range:** Clamped to [20, 85] (preserves realism — never predicts 0 or 100 from quiz alone).

**Where Clamping Occurs:**
- `applyTaskEffect`: `Math.min(currentScore + 0.5, 100)` — caps at 100, no floor check needed (drift is always positive).
- `photoAnalyser.clampAnalysis()`: All 9 pillar scores clamped [0, 100], all deltas clamped [-100, 100].
- `quizScoreEstimator`: Each pillar estimate clamped [20, 80], final score clamped accordingly.

**Acceptance Criteria:**
- AC-6.1: Pillar scores never exceed 100.
- AC-6.2: Pillar scores never go below 0.
- AC-6.3: Negative deltas allowed (up to -100).
- AC-6.4: Estimator never predicts below 20 or above 85.
- AC-6.5: Optimisation score stays within 0-100.

---

### 4.7 Progress Store

**Implementation:** `src/store/progressStore.ts` + `src/hooks/useProgress.ts`

Zustand store holding all score-related state. Hydrated from Supabase `progress` table on app boot and refreshed after score-affecting events.

**Store State:**
```typescript
interface ProgressStoreState {
  // Raw progress table fields
  totalXP: number
  level: number
  levelName: string
  xpToNextLevel: number
  currentStreak: number
  longestStreak: number
  optimisationScore: number

  // Computed from progress table
  pillarScores: PillarScores

  // Meta
  isLoading: boolean
  error: string | null

  // Hydrate all progress data from Supabase
  refreshAll: (userId: string) => Promise<void>
}
```

**Hydration:**
- `refreshAll(userId)` called on `useProgress` hook mount (when `user.id` is available).
- Fetches `progress` row for user: all 9 pillar score columns, `optimisation_score`, `total_xp`, `level`, `current_streak`, `longest_streak`.
- Computes `pillarScores` by mapping column values into `PillarScores` type with deltas (score - 50 baseline).
- Sets `isLoading = false` when complete.

**Refresh Triggers:**
- After task completion (via `taskEngine.completeTask` → store refresh).
- After cycle check-in (via `cycle.updateCycleWithAnalysis` → store refresh).
- After first strike completion (via `firstStrikeService.completeFirstStrike` → store refresh).
- On app foreground (via `AppState` listener in `app/_layout.tsx`).

**useProgress Hook:**
- Returns reactive data from the progress store.
- Computes `deltaVsBaseline` as `optimisationScore - 50`.
- Writes shared state for iOS widgets via `writeSharedState({ forgeScore, programDay })`.

**Acceptance Criteria:**
- AC-7.1: Progress store hydrated from Supabase on app boot.
- AC-7.2: Pillar scores reflect database values.
- AC-7.3: Deltas correctly computed as `score - 50`.
- AC-7.4: Store refreshed after task completion.
- AC-7.5: Store refreshed after cycle check-in.
- AC-7.6: `deltaVsBaseline` accurately reflects current vs baseline.
- AC-7.7: Shared state written for iOS widgets.
- AC-7.8: Loading state managed during hydration.
