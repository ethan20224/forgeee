# Feature: Onboarding Flow

**Actor:** Guest → User (Member)
**Phase:** MVP ✅ Done
**Related flows:** [onboarding-flow.md](../flows/onboarding-flow.md), [sign-in-flow.md](../flows/sign-in-flow.md)
**Implementation:** `app/(auth)/*`, `src/hooks/useOnboarding.ts`, `src/hooks/usePlanGeneration.ts`, `src/services/ai/planGenerator.ts`, `src/lib/quizCache.ts`, `src/lib/planCache.ts`

## Purpose

Convert a curious visitor into a paying subscriber with a personalised 90-day plan. The onboarding flow balances showing value early (quiz → estimated score → plan reveal) before requiring payment. Baseline photo is deferred to day 3 — removing friction from the signup funnel.

## State Machine

```
splash → welcome → quiz (7 steps) → estimated-score → signup → plan-loading → plan-reveal → paywall → /(app)
                                                                                                      │
                                                                                             (day 3 after start)
                                                                                                      │
                                                                                            baseline-photo prompt
```

## Subsections

### 1.1 Welcome Carousel

**Screen:** `app/(auth)/welcome.tsx`

Three horizontally-paginated animated slides introducing FORGE's value proposition. Uses `react-native-reanimated` for slide transitions (opacity + translateX transforms only — no heavy animations).

**Slides:**
1. **Tagline:** "Your appearance, optimised by AI." — Explains the 90-day structured program concept with a dark aesthetic illustration of a man's silhouette with glowing pillar indicators.
2. **Method:** "7 questions. 1 plan. 1 Season." — Shows the quiz-to-plan pipeline visually. Mentions 9 pillars of appearance.
3. **Result:** "A version of you that already exists." — Emphasises the transformation is unlocking potential, not creating something fake. CTA: "See Your Blueprint" button.

**Behaviour:**
- Slide dots indicator at bottom tracking current position.
- "Skip to Quiz" text link always visible in top-right corner.
- PostHog events: `WELCOME_VIEWED` on mount, `WELCOME_SLIDE_VIEWED` with `slide_index` on each slide change.
- On mount, checks AsyncStorage for a saved quiz draft. If draft exists, shows a "Resume Quiz" banner above the slides. Draft is stored as `forge_quiz_draft` key with shape `{ answers: Partial<QuizAnswers>, currentStep: number, lastSaved: string }`.
- Auto-advance timer (6 seconds per slide) — pauses on user interaction.

**States:** Loading (session check), content (slides), error (N/A — no async data).

**Acceptance Criteria:**
- AC-1.1: All 3 slides render with correct copy and animations.
- AC-1.2: Slide indicator updates correctly on swipe and auto-advance.
- AC-1.3: `WELCOME_VIEWED` fires exactly once on mount.
- AC-1.4: `WELCOME_SLIDE_VIEWED` fires on each slide change with correct `slide_index`.
- AC-1.5: "Skip to Quiz" navigates to `/(auth)/quiz`.
- AC-1.6: Quiz draft resume banner appears when `forge_quiz_draft` exists in AsyncStorage.
- AC-1.7: Tapping resume banner navigates to quiz at saved step.
- AC-1.8: Resume banner is hidden when no draft exists.

---

### 1.2 Quiz

**Screen:** `app/(auth)/quiz/index.tsx`, `app/(auth)/quiz/[step].tsx`

7 questions presented as individual steps navigated via Expo Router dynamic route `/(auth)/quiz/[step]`. Uses `useOnboarding` hook for state management.

**Questions (in order):**
1. **Goals** (multi-select): skin, grooming, fitness, style, confidence, all — stored as `goals: string[]`
2. **Main Concern** (single-select): skin, hair, grooming, posture, style — stored as `mainConcern: string`
3. **Current Routine** (single-select): none, basic, moderate, advanced — stored as `routineLevel: string`
4. **Daily Time** (single-select): 5min, 15min, 30min, 1hr — stored as `dailyTime: string`
5. **Commitment Timeline** (single-select): 30days, 90days, 6months, 1year — stored as `timeline: string`
6. **Age Range** (single-select): 18-24, 25-30, 31-40, 41-50, 51+ — stored as `ageRange: string`
7. **Confirmation** — review summary of all answers, "Generate My Plan" CTA.

**Behaviour:**
- Answers cached at each step to `zustand` store (`useProgramStore.quizAnswers`) AND persisted to AsyncStorage as `forge_quiz_draft` on every answer change (debounced 500ms).
- Step navigation: "Back" text link (top-left), progress bar (top), question content (centre), option cards (centre-bottom). Progress bar shows `currentStep/7`.
- Each option is a `ForgeCard` with title + optional subtitle. Selected card gets teal border (`Colors.progress = #00C4A7`).
- PostHog events: `QUIZ_STARTED` on quiz index mount, `QUIZ_STEP_COMPLETED` on each step advance with `{ step_number, answer }`, `QUIZ_COMPLETE` on final step.
- 7th step (confirmation) shows all answers in a review layout. Each answer is editable — tapping navigates back to that step. "Generate My Plan" navigates to `estimated-score`.

**States:** Loading (initial route), content (quiz step), empty (N/A).

**Acceptance Criteria:**
- AC-2.1: All 7 questions render with correct options and UI.
- AC-2.2: Progress bar updates correctly (1/7 through 7/7).
- AC-2.3: Back navigation returns to previous step; at step 1, goes to welcome.
- AC-2.4: Answers persist to AsyncStorage on each change (verify via `forge_quiz_draft` key).
- AC-2.5: `QUIZ_STARTED` fires once on quiz entry.
- AC-2.6: `QUIZ_STEP_COMPLETED` fires on each step advance with correct payload.
- AC-2.7: `QUIZ_COMPLETE` fires on final step with all quiz answers in properties.
- AC-2.8: Confirmation screen shows all 6 answers, each tappable to edit.
- AC-2.9: Quiz draft is deleted from AsyncStorage after quiz completion.
- AC-2.10: App kill mid-quiz → draft survives → resume on next launch.

---

### 1.3 Estimated Score

**Screen:** `app/(auth)/estimated-score.tsx`

Psychological hook displayed before signup. Uses `quizScoreEstimator.ts` to compute a predicted FORGE Optimisation Score from quiz answers. This screen serves as the "you're here → you could be there" moment.

**Behaviour:**
- Calls `estimateScoreFromQuiz(answers)` which returns `{ estimated, rangeLow, rangeHigh, pillarEstimates }`.
- Displays estimated score as a large animated number (count-up from 0 to estimated value over 1.5 seconds).
- Shows range: "Your starting point: {rangeLow} – {rangeHigh}"
- Shows top 3 weakest pillars with their estimated scores and one-line description.
- "Create Account to See Full Blueprint" CTA → navigates to signup.
- Back link: "Back to Quiz" → returns to quiz confirmation step.

**Score Estimator Logic** (`quizScoreEstimator.ts`):
- Base score: 50 for all pillars.
- Routine level delta: none=-10, basic=-3, moderate=+2, advanced=+6 (applied to skin, grooming, hair).
- Main concern delta: specific pillars reduced (-3 to -10 range) based on concern.
- Daily time delta: 5min=-3, 15min=0, 30min=+3, 1hr=+5.
- Timeline delta: 30days=0, 90days=+2, 6months=+4, 1year=+6.
- Goal-based adjustments: each selected goal modifies its pillar.
- All estimates clamped to 20-80 range.
- Final score: weighted average across 9 pillars using fixed estimator weights.

**States:** Loading (score calculation), content (score display), error (invalid quiz data).

**Acceptance Criteria:**
- AC-3.1: Estimated score displays as animated count-up.
- AC-3.2: Score range (low-high) is within 20-85 bounds.
- AC-3.3: Top 3 weakest pillars shown with their estimated values.
- AC-3.4: "Create Account" CTA navigates to signup screen.
- AC-3.5: "Back to Quiz" returns to quiz confirmation (step 7).
- AC-3.6: Page renders nothing if quiz answers are missing (redirect to quiz).

---

### 1.4 Plan Loading

**Screen:** `app/(auth)/plan-loading.tsx`

Animated loading screen displayed while Codex AI generates the user's 90-day plan. Uses a minimum 4-second display to prevent flicker even if generation is fast.

**Behaviour:**
- Calls `planGenerator.generatePlan(quizAnswers)` via `usePlanGeneration` hook.
- Displays a looping animation (gradient pulse on a ForgeCard skeleton) with rotating coaching messages.
- 4 rotating messages (switched every 2 seconds):
  1. "Analysing your goals..."
  2. "Building your 90-day architecture..."
  3. "Selecting the right tasks for your foundation..."
  4. "Almost ready — calibrating intensity..."
- Progress indicator (indeterminate bar with teal colour).
- On success: stores generated plan in `planCache.ts` (`setCachedPlan(plan)`), navigates to `/(auth)/plan-reveal`.
- On error: displays error message with "Try Again" button. `PLAN_GENERATION_FAILED` PostHog event fires with `error_message`.
- Minimum display time enforced: if generation completes in < 4 seconds, the animation continues until 4 seconds total have elapsed.
- PostHog: `PLAN_GENERATING` fires on screen mount.

**Plan Generator** (`planGenerator.ts`):
- Sends quiz answers + full Task Library JSON to Claude via `claude-proxy` edge function.
- System prompt enforces: use `libraryTaskId` from library only, structure as 13 weeks × 7 days × 2-5 tasks each.
- Validates response: checks programName, focusSummary, honestExpectation present; all task libraryTaskIds exist in library; week/day/task structure complete.
- Returns `GeneratedPlan` with `{ programName, focusSummary, honestExpectation, weeks[], milestones[] }`.

**States:** Loading (animation), content (N/A — auto-navigates on success), error (message + retry).

**Acceptance Criteria:**
- AC-4.1: Loading animation displays for minimum 4 seconds.
- AC-4.2: All 4 rotating messages display in sequence.
- AC-4.3: On success, plan is stored in `planCache` and screen navigates to plan-reveal.
- AC-4.4: On error, error message is displayed with "Try Again" button.
- AC-4.5: `PLAN_GENERATING` fires on mount.
- AC-4.6: `PLAN_GENERATION_FAILED` fires on error with `error_message`.
- AC-4.7: Try Again re-initiates generation and resets states.
- AC-4.8: Generated plan validates successfully against all structural requirements.

---

### 1.5 Plan Reveal

**Screen:** `app/(auth)/plan-reveal.tsx`

Displays the AI-generated plan for user review before commitment. The user sees what they'll get over 90 days. "Start Transformation" commits the plan to the database.

**Behaviour:**
- Reads plan from `planCache` via `getCachedPlan()`. If cache is empty, redirects to plan-loading (edge case: direct navigation).
- Displays:
  - **Program Name** — large display text (`Typography.display = 32`).
  - **Honest Expectation** — 1-2 sentence realistic outcome statement.
  - **Focus Areas** — 2-3 bullet points showing program emphasis.
  - **Expected Results** — 1-2 sentences on what user should see.
  - **Daily Time Commitment** — derived from quiz `dailyTime` answer.
  - **Milestones** — timeline of 3-4 key program milestones (day 7, day 30, day 60, day 90).
- "Start Transformation" PrimaryButton (gold `#E8A400`).
  - On press:
    1. Calls `savePlan(plan)` → `savePlanToDatabase(userId, plan)` which inserts plan row + all daily_tasks rows + task_library_selections.
    2. Calls `completeOnboarding(planStartDate)` which sets `users.onboarded = true` and `users.plan_start_date = today`.
    3. Navigates to `/(auth)/paywall`.
- If user already has a baseline analysis cached (edge case: mid-onboarding recovery flow), displays the onboarding compliment from `compliPrompt`.
- Any database error shows user-readable error with retry.

**States:** Loading (plan fetch from cache), content (plan display), empty (no cached plan → redirect), error (DB save failure).

**Acceptance Criteria:**
- AC-5.1: Plan renders correctly with program name, expectation, focus areas, milestones.
- AC-5.2: "Start Transformation" saves plan to database (verify plans + daily_tasks rows created).
- AC-5.3: `onboarded` flag set to `true` and `plan_start_date` set after save.
- AC-5.4: Navigation to paywall occurs after successful save.
- AC-5.5: Empty cache redirects to plan-loading with no error.
- AC-5.6: DB save error shows user-readable message with retry.
- AC-5.7: Onboarding compliment displays if baseline analysis is cached.
- AC-5.8: `PLAN_REVEALED` PostHog event fires with `plan_name` on mount.

---

### 1.6 Paywall

**Screen:** `app/(auth)/paywall.tsx`

Full-screen RevenueCat paywall converting the user to a paid subscriber. Single Basic tier at $11/mo.

**Behaviour:**
- Calls `useSubscription` hook for purchase flow.
- Displays:
  - **Hero section** — "Your Blueprint is Ready" heading with plan name subtitle.
  - **Feature list** — 4-5 bullet points: personalised 90-day plan, daily task guidance, AI photo check-ins every 3 days, weekly coaching reports, FORGE Optimisation Score tracking.
  - **Pricing card** — "$11/month" prominent. "3-day free trial" indicator if available from RevenueCat offering.
  - **Primary CTA** — "Unlock Your Blueprint" button (gold `#E8A400`). Calls `purchase()`.
  - **Secondary link** — "Maybe later" text link (low-contrast `Colors.textSecondary = #5A5A5A`). Sets `onboarded=true` without payment (dev only; production requires purchase).
- Purchase flow:
  1. `configure(userId)` called in `app/_layout.tsx` on boot with Supabase user ID.
  2. `purchase()` calls `Purchases.purchasePackage(basicPackage)`.
  3. On success: requests notification permissions, schedules all notifications via `useNotifications.scheduleAll()`, navigates to `/(app)/(tabs)`.
  4. On cancellation: stays on paywall. On error: displays error with retry.
- **Dev bypass:** When `__DEV__` is true and `EXPO_PUBLIC_APP_ENV !== 'production'`, "Maybe later" sets `subscription_tier = 'basic'` and navigates to app directly. This is for development testing only.
- PostHog: purchase events handled by RevenueCat webhook (server-side).

**States:** Loading (RevenueCat products fetching), content (paywall display), error (purchase failure with retry).

**Acceptance Criteria:**
- AC-6.1: Pricing displays correct $11/mo amount from RevenueCat.
- AC-6.2: Feature list shows 4-5 accurate bullet points.
- AC-6.3: Purchase initiates RevenueCat flow successfully.
- AC-6.4: On successful purchase, notification permissions requested and scheduled.
- AC-6.5: On successful purchase, navigates to `/(app)/(tabs)`.
- AC-6.6: "Maybe later" navigates without purchase in dev mode only.
- AC-6.7: Purchase error shows user-readable message with retry.
- AC-6.8: Free trial indicator shows when available from RevenueCat offering.
- AC-6.9: RevenueCat configure() called before paywall renders.

---

### 1.7 Signup / Login

**Screen:** `app/(auth)/signup.tsx`

Email + password authentication via Supabase Auth. Single screen with tab toggle between Sign Up and Sign In modes.

**Behaviour:**
- Tab toggle at top: "Sign Up" / "Sign In" segmented control.
- **Sign Up mode:**
  - Email field, password field, confirm password field.
  - Client-side validation: email format (regex), password ≥ 8 chars, passwords match.
  - Server-side: calls `signUp(email, password)` via `src/lib/auth.ts`.
  - On success: Supabase creates auth user, `users` row created via trigger or subsequent insert. `plan_start_date` captured on signup (not on login). `timezone` captured via `Intl.DateTimeFormat().resolvedOptions().timeZone`.
  - PostHog: `SIGNUP` event with `{ method: 'email' }`.
- **Sign In mode:**
  - Email field, password field.
  - Calls `signIn(email, password)`.
  - On success: auth state listener in `_layout.tsx` picks up session and routes to correct screen based on `onboarded` flag.
- **Ghost user recovery:** If a user signs up with an email that already has an auth account but no `users` row (ghost), the signup flow detects this and creates the `users` row instead of returning an error.
- Error messages: "Email already registered" (signup), "Invalid login credentials" (signin), "Network error — please check your connection".
- "Forgot password?" link (future — not implemented in MVP).
- PostHog: `SIGNUP_VIEWED` on screen mount.

**States:** Loading (auth call in progress), content (form), error (validation/server errors).

**Acceptance Criteria:**
- AC-7.1: Toggle switches between Sign Up and Sign In forms correctly.
- AC-7.2: Client-side email validation rejects invalid formats.
- AC-7.3: Client-side password validation rejects < 8 characters.
- AC-7.4: Confirm password mismatch shows inline error.
- AC-7.5: `signUp` creates Supabase auth user and `users` row.
- AC-7.6: `signIn` authenticates and routes to correct screen based on `onboarded`.
- AC-7.7: Timezone captured and saved on signup.
- AC-7.8: Ghost user recovery creates `users` row for existing auth users.
- AC-7.9: `SIGNUP_VIEWED` fires on screen mount.
- AC-7.10: `SIGNUP` fires on successful signup with correct payload.

---

### 1.8 Auth Guards

**Implementation:** `app/_layout.tsx`

Root layout component that monitors authentication state and routes users to the correct screen.

**Behaviour:**
- `onAuthStateChange` listener from Supabase monitors session changes.
- Attempts `getSession()` on mount as fallback for cold starts.
- **Routes:**
  - No session + no `users` row → `/(auth)/splash`
  - Session exists + `onboarded = false` → check `plan_start_date`:
    - No `plan_start_date` → `/(auth)/welcome` (fresh start)
    - `plan_start_date` exists → check if plan exists in DB:
      - Plan exists + `plan_start_date` is today → `/(auth)/plan-reveal` (crash recovery)
      - Plan exists + `plan_start_date` is past → `/(auth)/paywall` (paywall skip recovery)
      - No plan → `/(auth)/plan-loading` (regenerate)
  - Session exists + `onboarded = true` → `/(app)/(tabs)/` (main app)
- Loading state: shows splash screen while auth state resolves.
- On sign out: calls `userStore.reset()`, `programStore.reset()`, `progressStore.reset()`. Clears all Zustand stores.
- Baseline photo is NOT required for app entry — it is prompted in-app on day 3 via `app/(app)/baseline-photo.tsx`.
- Retries pending task effects on mount via `retryPendingEffects(userId)`.

**Acceptance Criteria:**
- AC-8.1: Fresh install → splash → auth check → routes to welcome.
- AC-8.2: Signed in + onboarded → goes directly to main app tabs.
- AC-8.3: Signed in + not onboarded + no plan → routes to welcome.
- AC-8.4: Signed in + not onboarded + plan exists → routes to correct recovery screen.
- AC-8.5: Sign out clears all stores and redirects to splash.
- AC-8.6: No baseline photo required for app entry.
- AC-8.7: Pending task effects retried on mount.
- AC-8.8: Auth state loading shows splash screen (not blank white).

---

### 1.9 Quiz Draft Persistence

**Implementation:** AsyncStorage key `forge_quiz_draft`, debounced writes in quiz steps.

**Behaviour:**
- On each quiz answer change, the full quiz state is written to AsyncStorage with debounce (500ms).
- Draft structure: `{ answers: Partial<QuizAnswers>, currentStep: number, lastSaved: ISO string }`.
- On welcome screen mount: reads `forge_quiz_draft`. If exists and `lastSaved` is < 7 days ago, shows resume banner.
- Resume: navigates to quiz at `currentStep`. Restores `answers` into Zustand store.
- On quiz completion: deletes `forge_quiz_draft` from AsyncStorage.
- On signup: deletes `forge_quiz_draft` (cleanup — user has committed).
- On sign out: deletes `forge_quiz_draft` (fresh start for next session).

**Acceptance Criteria:**
- AC-9.1: Quiz answers persist across app kills.
- AC-9.2: Resume banner appears on welcome screen when draft < 7 days old.
- AC-9.3: Resume restores quiz to correct step with filled answers.
- AC-9.4: Draft deleted on quiz completion.
- AC-9.5: Draft deleted on signup.
- AC-9.6: Draft deleted on sign out.
- AC-9.7: Drafts older than 7 days are ignored (shown as "Start Fresh" instead).
