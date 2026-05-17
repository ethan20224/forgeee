# FORGE Design Specification

> Complete design language, screen specifications, and user flows for the FORGE mobile application. Source of truth for all visual and interaction design decisions.

---

## Design Tokens

```yaml
# ── Tailor's Chalk Design System (April 2026) ───────────────────────
# Source of truth: src/constants/design.ts

colors:
  # Surface hierarchy (warm charcoal)
  canvas:       "#0A0907"     # deepest background
  surface:      "#100E0C"     # main surface / cards
  raised:       "#181513"     # elevated elements
  raisedHi:     "#1F1A16"     # highest elevated
  divider:      "#251F1A"     # separators

  # Text hierarchy (warm off-white progression)
  bone:         "#F2EEE7"     # primary text
  ash:          "#8A7D72"     # secondary text
  muted:        "#5C544B"     # tertiary text

  # Primary accent (ember — burnt orange)
  ember:        "#C4543A"     # primary accent / CTAs
  emberDim:     "rgba(196,84,58,0.12)"   # background tint
  emberBorder:  "rgba(196,84,58,0.20)"   # border variant

  # Secondary accent (brass — warm gold)
  brass:        "#B89F7E"     # warm gold accent

  # Legacy tokens (deprecated, mapped to new values)
  bg:           "#0A0A0A"     # @deprecated Use Colors.canvas
  teal:         "#C4543A"     # @deprecated Use Colors.ember
  gold:         "#E8A400"     # legacy gold
  danger:       "#E84545"     # error states
  dangerDim:    "rgba(232,69,69,0.12)"

  # 9-pillar colors
  facial:       "#64B5F6"     # facial composition — light blue
  skin:         "#00C4A7"     # skin — teal
  grooming:     "#9B8EFF"     # grooming — lavender
  hair:         "#FFAB76"     # hair — peach
  posture:      "#FF8A65"     # posture — coral
  style:        "#E8A400"     # style — gold
  sleep:        "#7986CB"     # sleep — indigo
  nutrition:    "#81C784"     # nutrition — green
  voice:        "#CE93D8"     # voice — mauve
  lifestyle:    "#5A8A6A"     # lifestyle — forest

typography:
  fontFamily: Inter (primary), SpaceGrotesk-Bold (display/wordmark)
  scale:
    hero:       { size: 64, weight: 700, letterSpacing: -2.2, lineHeight: 1.1 }  # main score displays
    display:    { size: 32, weight: 700, letterSpacing: -0.64, lineHeight: 1.1 } # section headings
    title:      { size: 24, weight: 700, lineHeight: 1.3 }                        # sub-headings
    heading:    { size: 17, weight: 700, lineHeight: 1.3 }                        # card headings
    body:       { size: 17, weight: 400, lineHeight: 1.55 }                       # body text
    caption:    { size: 13, weight: 400, lineHeight: 1.55 }                       # captions
    label:      { size: 11, weight: 700, lineHeight: 1.55 }                       # labels / micro-text
    micro:      { size: 11, weight: 400, letterSpacing: 0.44 }                    # monospaced labels
    nano:       { size:  9, weight: 700, lineHeight: 1.55 }                       # data suffixes / eyebrows
  weights: [300, 400, 500, 700, 800]
  lineHeights:
    tight: 1.1
    normal: 1.55
    relaxed: 1.6

borderRadius:
  none: 0
  sm: 2                   # sharp architectural
  md: 4
  lg: 8
  card: 12
  xl: 20
  full: 999

spacing:
  xs: 2
  sm: 4
  md: 8
  lg: 16
  xl: 24
  xxl: 32
  xxxl: 48
  screen: 24              # horizontal screen padding

animation:
  fast: 150
  normal: 250
  slow: 400
  spring: 350

easing:
  entrance:   "cubic-bezier(0.16, 1, 0.3, 1)"
  resolution: "cubic-bezier(0.4, 0, 1, 1)"
  state:      "cubic-bezier(0.4, 0, 0.2, 1)"

spring:
  gentle: { damping: 20, stiffness: 100 }
  snappy: { damping: 15, stiffness: 200 }
  bouncy: { damping: 10, stiffness: 150 }
```

---

## Project Goals

### Objective

Deliver a 90-day appearance transformation program for men that feels premium, data-driven, and trustworthy — never gimmicky.

### Target Audience

Men aged 19–40 who want to improve their appearance but don't know where to start or have plateaued.

### Core Problem

No objective, measurable way to track appearance improvement over time, combined with overwhelming, untrustworthy product advice. FORGE solves this by providing a quantitative, AI-powered scoring system across 9 measurable pillars of appearance, paired with a structured 90-day program of curated, evidence-backed tasks.

### Design Principles

1. **Pillar-first everything** — The 9 pillars are the atomic unit of measurement, coaching, and plan structure. Every task maps to a pillar. Every score change is pillar-granular. Every coaching insight references pillar movement.
2. **Flat dark surfaces, no shadows** — Deep charcoal backgrounds with opacity-bordered cards. No drop shadows, no elevations, no gradients (except animated mesh gradients for depth on splash/score displays). Teal only for scores. Ember only for CTAs.
3. **Onboarding defers friction** — Baseline photo is prompted on day 3 when the user is invested, not during signup. Quiz happens before account creation. Users see value before committing.
4. **Every screen handles 3 states** — Loading (skeleton/spinner), content (data present), and empty/error (actionable message with retry). No blank white states.
5. **Notifications use factual reassurance, never guilt** — "Cycle photo today. Same angle, same lighting." Not urgency, FOMO, or shaming.

---

## Key User Flows

### Flow 1: Onboarding

1. **Splash** — App opens to splash screen. Animated FORGE wordmark (SpaceGrotesk-Bold, 64px) fades in over a dark canvas with SVG grain texture overlay and animated mesh gradient. A thin progress bar indicates app initialisation (auth check, Supabase session recovery). Transitions to welcome after ~2s or when auth state resolves.
2. **Welcome Carousel** — Three horizontally-paginated slides with slide-from-right transitions. Slide 1: "THE TRUTH" — appearance is measurable, not subjective. Slide 2: "THE SCIENCE" — 28-day skin renewal, 66-day habit formation, 90-day transformation. Slide 3: "WHAT WE CAN CHANGE" — locked vs. optimisable traits, the 9 pillars. Each slide has a bold title, supporting body text, and a dot indicator. "Continue" button on the final slide navigates to quiz.
3. **Quiz** — 7-step quiz with horizontal progress bar at the top. Each step is a single question with 2–5 tappable option cards. Slide-from-right animation between steps. Questions cover: goals, current routine, time availability, timeline expectations, main concern, age range, and face shape self-assessment. Answers are cached in-memory (quizCache) and persisted to AsyncStorage as a draft. Back-arrow on every step except the first. Skip allowed on optional questions. After the final question, navigate to estimated score.
4. **Estimated Score** — A full-screen score reveal screen. Large animated number (64px hero size, teal) counts up from 0 to the estimated FORGE Score. Below: a short subtext like "Based on your current routine and goals." A "Your Journey Starts Now" CTA navigates to signup. The estimated score is generated by `deriveInitialWeights()` from quiz answers and stored in the quiz cache for plan generation context.
5. **Signup** — Clean single-screen form. Inputs: Name (bone text on surface background with border), Email (same style, email keyboard type), Password (same style, secure entry). Full-width ember PrimaryButton: "Create Account". Below: "Already have an account? Log in" link navigates to login variant screen (same layout, toggles to "Log In" button). Error states: inline validation errors below each input (danger text). On success: Supabase Auth creates user, triggers referral code auto-generation, navigates to plan-loading.
6. **Plan Loading** — Full-screen loading experience. Centered animated ring spinner in teal. Below the spinner: rotating coaching messages (~8 messages cycling every 2.5s) such as "Building your personalised plan...", "Analysing your goals...", "Selecting tasks from the Master Library...". Background has mesh gradient and grain overlay for depth. In the background, `planGenerator.ts` calls Codex AI with the quiz answers and Master Task Library context to generate a 90-day plan structured as 12 weeks × 7 days × 2–5 tasks. The generated plan is cached in-memory (planCache). On success, navigates to plan-reveal. On error, shows an error state with retry.
7. **Plan Reveal** — Scrollable screen showing the personalised plan. Top section: program name (title size, bone), estimated score (hero size, teal), focus areas (pillar badges in their respective colors). Middle section: expected improvements per pillar with visual progress indicators, daily time commitment (typically 15–30 min). Bottom section: AI-generated onboarding compliment (15–25 word strength callout). Fixed-bottom ember PrimaryButton: "Start Transformation" — saves the plan to the `plans` table, sets `onboarded=true` and `plan_start_date` on the `users` table, then navigates to paywall.
8. **Paywall** — Full-screen subscription gate. Top: FORGE wordmark (SpaceGrotesk-Bold, 32px). Feature list in checklist format (bone text, teal checkmarks): "Personalised 90-day plan", "AI photo check-ins every 3 days", "Weekly coaching reports", "FORGE Score tracking across 9 pillars". Price: "$11/mo" in hero size bone. Free trial indicator: "Try 3 days free, then $11/mo. Cancel anytime." Ember PrimaryButton: "Start Free Trial" — calls RevenueCat's `purchase()` for the Basic tier package. Below: "Restore Purchase" link (SecondaryButton style). On purchase success: navigates to notification permission request, then schedules all 3 notification types (day-1 welcome push, cycle reminders, weekly report notifications), then navigates to `/(app)`.
9. **Main App Entry** — User lands on the Home tab. The onboarding flow is complete. Baseline photo will be prompted on day 3 via an in-app modal and persistent banner.

### Flow 2: Daily Routine

1. **Open App** — Home tab loads. Status strip at top: streak count with fire icon (ember), FORGE Optimisation Score (teal, 24px), current phase name from `PHASE_DISPLAY` (caption, ash). AI insight card below the status strip with the daily coaching tip (≤25 words, body size, bone text on raised background).
2. **Task List** — 2–5 task cards for today. Ordered: incomplete tasks first, sorted by duration (shortest first), then completed tasks at bottom with checkmarks and strikethrough. Each `TaskCard` shows: task title (outcomeTitle when day < 57, else clinical title), pillar badge (colored dot + label in pillar color), duration (min), XP value badge, and a completion checkbox/button.
3. **Task Detail** — Tapping a task navigates to `task/[taskId]`. Shows: task title (heading size), pillar badge with full color background, duration and XP value, "Why It Works" explanation card (body text on raised surface, expanded by default when day ≥ 29 per `showWhyByDefault()`), and a full-width ember "Mark Complete" button. If task is already completed, the button is replaced with a checkmark icon and "Completed" label.
4. **Complete Task** — Tapping "Mark Complete": button animates to a checkmark, XP awarded (10 base + 20 streak bonus if `current_streak > 3`), XP bar animates upward, streak updated via `updateStreak()`, pillar score drifts +0.5 via `applyTaskEffect()`. If this is the user's first-ever task (tracked via `users.first_strike_completed`), the First Strike modal appears: celebration animation with micro-score, AI-generated insight compliment, and "Continue" button. If all today's tasks are completed, the "all done" celebration appears: animated checkmark, "All Done for Today" message, and a summary of total XP earned.
5. **Pull to Refresh** — Dragging down on the home screen reloads today's tasks and the daily insight from Supabase.

### Flow 3: Cycle Check-In (every 3 days)

1. **Prompt** — On program days 3, 6, 9, 12, etc. (every 3 days), the app receives a push notification and shows an in-app banner: "Cycle photo today. Same angle, same lighting." Tapping the banner or navigating to the Cycle tab opens the cycle screen.
2. **Camera Viewfinder** — Full-screen camera viewfinder (`expo-camera`) with a face guide overlay (white outline ellipse indicating where to position the face). "Face mode" is the default scan mode — captures front-facing photo only (style, sleep, nutrition, voice pillars set to data_gap/null). Toggle to "Full mode" requires left + right profile photos (all pillars analysed). Flash toggle, camera flip button.
3. **Capture** — Single front-facing photo taken. Photo crops to 3:4 portrait aspect ratio, compresses to ≤500KB via `imageService.compress()`. User reviews the photo with retake/use options.
4. **Upload & Analyse** — Photo uploaded to private Supabase bucket (`user-photos-private`) via `imageService.upload()`. A signed URL is generated with 3600s expiry via `getSignedPhotoUrl()`. The signed URL is sent to Codex Vision (`callClaudeVision()`) with face scan mode context, previous cycle scores for delta calculation, and the user's face shape. The system prompt lives in `src/services/ai/prompts/photoPrompt.ts`.
5. **Results Display** — `CycleAnalysis` returned with: 9 pillar scores (0–100 each), overall FORGE score, primary insight (1 sentence), next focus area (pillar name + coaching direction). Results rendered on the `CycleResultCard`: pillar scores as horizontal progress bars (pillar color fill, bone text score), overall score as hero teal number, insight text in a raised card, next focus pill with ember border accent.
6. **Save** — Cycle saved to the `cycles` table with auto-incremented `cycle_number` via database trigger. The `progress` table is updated with the new pillar scores and optimisation score.
7. **Photo Timeline** — The new photo appears in the photo timeline screen (`photo-timeline`), displayed as a card in a reverse-chronological vertical scroll. Each card shows the cycle number, date, and a thumbnail. Tapping a card opens the full cycle result.

### Flow 4: Season Complete (Day 90)

1. **Detection** — When the user completes their tasks for day 90, the program advancement check (`advanceProgramDay()`) detects that `program_day >= 90` and the user is on day 90 of the season. Triggers the season complete flow.
2. **Season Complete Screen** — Full-screen animated celebration. Mesh gradient background animates. Hero text: "Season 1 Complete" in SpaceGrotesk-Bold. Below: before/after score comparison — starting FORGE Score on the left (muted, dimmed), final FORGE Score on the right (teal, hero size, animated count-up). Delta displayed with a "+X" badge in teal. Below score: pillar movement summary — each pillar listed with its starting score, ending score, and delta.
3. **AI Season Report** — Generated by `generateSeasonReport()` in `coachingEngine.ts`. A narrative story format markdown report (400–600 words) covering: the user's starting point, key breakthrough moments (largest pillar movers), habits that stuck, pillars that plateaued, and a personalised focus for Season 2. Rendered in a scrollable `ForgeCard` with rich text (bone headings, ash body). Uses MECHANISM language stage (day 90 by definition).
4. **Review & Share** — User scrolls through the report. A share button (ember SecondaryButton) allows generating a season milestone share card via `useShareCard`. The card includes: final score, biggest mover pillar, season duration, and the FORGE wordmark.
5. **Season Rollover** — At the bottom, an ember PrimaryButton: "Start Season 2". On tap: triggers season rollover logic — updates `users.season` to 2, resets `users.program_day` to 1, generates a new 90-day plan with recalibrated pillar weights (incorporating cycle history data into the prompt), clears the old `daily_tasks` for the new season, and navigates to plan-reveal for Season 2.

---

## Screen Specifications

### (auth) Group — Onboarding & Authentication

#### 1. Splash (`app/(auth)/splash.tsx`)

**Purpose**: Branded loading screen that initialises the app, recovers auth state, and routes the user to the correct screen.

**Core Components**:
- `SplashScreen` — Full-screen dark canvas (`Colors.canvas`) with no status bar
- `AnimatedWordmark` — FORGE wordmark in SpaceGrotesk-Bold, 64px hero size, bone color, fade-in animation (400ms ease-out). Includes a subtle scale pulse (1.0 → 1.02 → 1.0) over 2s on loop
- `MeshGradientBackground` — Animated mesh gradient (subtle teal/ember blend at low opacity) behind the wordmark for depth
- `GrainOverlay` — SVG noise texture via `GRAIN_SVG` at 4.5% opacity over the entire screen
- `ProgressBar` — Thin horizontal bar (2px height, ember fill, muted track) near the bottom indicating app initialisation progress (auth check → session recover → route decision). Animates from 0 to 100% over ~2s
- `VersionLabel` — App version number in muted, 9px small size, bottom of screen

**Information Architecture**:
- Fetches: Supabase session via `supabase.auth.getSession()` and `supabase.auth.onAuthStateChange`
- Reads: `userStore.isAuthChecked` — prevents flash-of-wrong-screen
- Determines: if `user.onboarded === true` → route to `/(app)`; if authenticated but `onboarded === false` → route to correct onboarding step; if no session → route to `/(auth)/welcome`
- No data hooks needed — raw Supabase auth calls

**Functional Constraints**:
- Loading state: The splash screen itself IS the loading state (mesh gradient + wordmark + progress bar). No separate skeleton
- Error state: If auth check fails after 5 seconds (timeout), show "Something went wrong. Tap to retry." below the wordmark, with the progress bar frozen at its current position. Tapping retries `supabase.auth.getSession()`
- Empty state: N/A (splash always renders the same branded experience)
- Disabled state: N/A
- Conditional visibility: The progress bar only appears after the wordmark animation completes. The version label is always visible

---

#### 2. Welcome (`app/(auth)/welcome.tsx`)

**Purpose**: Introduce the FORGE brand and value proposition through three horizontally-paginated informational slides before the quiz.

**Core Components**:
- `WelcomeCarousel` — React Native `FlatList` with horizontal paging (`pagingEnabled`), snap-to-page scrolling
- `WelcomeSlide` (3 instances) — Each slide is a full-screen panel with:
  - Large ember or teal icon/badge at top (centered, 64px area)
  - Title in hero or title size, bone color, font weight 700
  - Body text in body size (13px), ash color, max width 280px, centered
  - Dot indicator row at bottom-center (3 dots: active dot = ember, inactive = muted)
- `GrainOverlay` — SVG noise texture across all slides for texture
- `SlideIndicator` — Row of 3 circular dots (8px diameter, 8px gap). Active dot: ember fill. Inactive dots: muted fill with 0.3 opacity. Animated transition between slides (scale + color, 250ms)
- `PrimaryButton` — Fixed at the bottom of the third slide only: "Continue" (ember background, bone text, full-width with `Spacing.screen` horizontal margins). Fades in when slide 3 is active
- `SkipLink` — Top-right corner: "Skip" in caption size, ash color. Navigates directly to quiz on tap

**Information Architecture**:
- No data fetching. Pure presentation screen
- No hooks needed. No store dependencies
- Slide content is hardcoded constants (localised text strings)

**Functional Constraints**:
- Loading state: N/A (static content, renders instantly)
- Empty state: N/A
- Error state: N/A (no network calls)
- Disabled state: The "Continue" button is hidden on slides 1 and 2, visible on slide 3
- Conditional visibility: Skip link visible on all slides. Continue button visible only on slide 3 (index 2). Dot indicator always visible

---

#### 3. Quiz Step (`app/(auth)/quiz/[step].tsx`)

**Purpose**: Collect 7 data points about the user's goals, routine, and preferences to personalise the AI-generated plan.

**Core Components**:
- `QuizProgressBar` — Horizontal bar at the top (8px height, full-width with screen padding). Fill: ember, track: muted. Percentage = current step / 7 * 100. Animated width transition (400ms ease-out) between steps
- `QuizStepIndicator` — Text label above the progress bar: "Step 3 of 7" in caption size, ash, right-aligned
- `QuizQuestion` — The question text in title size (24px), bone, font weight 700, top-left aligned with screen padding
- `QuizSubtext` — Optional supporting text below the question in caption size (11px), ash. Used for questions that need clarification
- `QuizOptionCard` (2–5 per step) — Tappable selection cards:
  - Background: `Colors.surface` with `Colors.divider` border (0.5px)
  - Selected state: `Colors.emberDim` background with `Colors.ember` border
  - Content: Option text in body size (13px), bone when unselected, bone when selected
  - Icon/emoji left-aligned within the card (24px)
  - 12px vertical padding, 16px horizontal padding, 8px border radius
  - Animated scale on press (0.98 → 1.0, 150ms)
- `QuizNavBar` — Top bar with: back arrow left (hidden on step 1), step indicator center, skip text right (on optional steps only)
- `AnimatedSlideTransition` — Slide-from-right animation (300ms, `Easing.entrance`) when navigating to next step. Slide-from-left when going back

**Information Architecture**:
- Reads/Writes: `quizCache` (module-level in-memory store + AsyncStorage persistence for drafts)
- No Supabase calls. No hooks. Pure client-side state
- Quiz answers stored as `QuizAnswers` type: `{ goals: string[], routine: string, timeBudget: string, timeline: string, mainConcern: string, ageRange: string, faceShapeSelf: string }`
- Steps are defined as a static array of question configs in `src/constants/quizQuestions.ts`

**Functional Constraints**:
- Loading state: N/A (static questions, renders instantly)
- Empty state: N/A
- Error state: N/A (no network calls during quiz)
- Disabled state: "Next" / navigation button is disabled until at least one option is selected (enabled state = ember background; disabled state = muted background, ash text). Back arrow is disabled on step 1 (hidden)
- Conditional visibility: Back arrow hidden on step 1. Skip link visible only on optional questions (steps with `optional: true`). Submit/CTA button visible on all steps, text changes on last step to "See My Score". Progress bar always visible

---

#### 4. Estimated Score (`app/(auth)/estimated-score.tsx`)

**Purpose**: Reveal the user's predicted starting FORGE Score based on quiz answers, creating a psychological hook before signup.

**Core Components**:
- `MeshGradientBackground` — Animated mesh gradient in teal tones for depth and drama
- `ScoreReveal` — Large hero-size (64px) teal number, SpaceGrotesk-Bold or weight 700. Animated count-up from 0 to the estimated score over 1.5s (ease-out). Letter-spacing: -2.2 (tight)
- `ScoreLabel` — Below the score: "Your estimated starting point" in caption size (11px), ash color, centered
- `ScoreSubtext` — Below the label: body text (13px), bone color, centered, max-width 280px. Text varies based on score range: high score = "You're already ahead. FORGE will take you further." mid = "Solid starting point. Let's unlock your potential." low = "Everyone starts somewhere. Your transformation begins now."
- `ScoreBreakdownPreview` — Horizontal row of 6 pill-shaped mini-badges, each showing an initial pillar estimate range (e.g. "Skin 40–50"). Pillar color background at 15% opacity, bone text in caption size. Animated fade-in with 100ms stagger delay each
- `PrimaryButton` — Full-width ember button: "Your Journey Starts Now" (title case, bone text, 17px). Fixed at the bottom of the screen with screen padding
- `SecondaryLink` — Below the button: "Not your score? Go back and retake the quiz" in caption size, muted, centered. Tapping navigates back to quiz step 1

**Information Architecture**:
- Reads: Quiz answers from `quizCache`
- Computes: Estimated score via `deriveInitialWeights()` in `src/services/scores/scoreCalculator.ts` — generates an initial estimate based on quiz input mappings (routine quality → base score, goals → pillar emphasis, age → baseline adjustment)
- Writes: Estimated score to `quizCache` for use in plan generation context
- No Supabase calls at this stage

**Functional Constraints**:
- Loading state: While the score calculation runs (~100ms), show a subtle shimmer on the score area (pulsing opacity animation on the number placeholder)
- Empty state: If quiz cache is somehow empty (user navigated directly to this screen), redirect back to quiz step 1
- Error state: If score calculation fails (unlikely for client-side math), show: "Couldn't calculate your score. Tap to try again." with a retry action
- Disabled state: The "Your Journey Starts Now" button is briefly disabled (500ms) during the count-up animation to ensure the user sees the score before tapping. Disabled state: muted background, ash text
- Conditional visibility: Score breakdown preview fades in after the score count-up animation completes. The "Not your score?" link appears after 2s delay

---

#### 5. Signup (`app/(auth)/signup.tsx`)

**Purpose**: Create a user account via email/password, or log in for returning users.

**Core Components**:
- `AuthHeader` — FORGE wordmark (SpaceGrotesk-Bold, 32px display size, ember). Below: "Create your account" in title size (24px), bone, centered. Below that: "Start your 90-day transformation" in caption size, ash
- `NameInput` — Text input for display name. Label: "Name" in small size (9px), weight 700, ash. Input field: body size (13px), bone text, surface background, border (1px, `Colors.border`), 12px border radius, 16px horizontal padding, 12px vertical padding. Focused state: ember border. Placeholder: "How should we call you?"
- `EmailInput` — Text input for email. Label: "Email" in small size, ash. Input field: same styling as name. Keyboard type: email-address. Auto-capitalize: none. Placeholder: "you@email.com"
- `PasswordInput` — Text input for password. Label: "Password" in small size, ash. Input field: same styling as name. Secure entry. Toggle visibility icon (eye/eye-off) on the right in muted color. Placeholder: "Min. 8 characters"
- `InlineError` — Red text (danger color) in caption size (11px) below the relevant input. Shows on blur validation or on submit error. Messages: "Please enter your name", "Enter a valid email", "Password must be at least 8 characters"
- `PrimaryButton` — Full-width ember button: "Create Account". Disabled state: muted background, ash text. Enabled state: ember background, bone text. Activates when all fields are non-empty and valid
- `AuthToggle` — Below the button: "Already have an account? Log in" in body size (13px). "Log in" is ember color, underlined. Tapping switches the screen to login mode
- `LoginMode` — When toggled to login: name input hides, button text changes to "Log In", header text changes to "Welcome back", subtext changes to "Pick up where you left off"

**Information Architecture**:
- Calls: `supabase.auth.signUp({ email, password, options: { data: { name } } })` for signup
- Calls: `supabase.auth.signInWithPassword({ email, password })` for login
- On signup success: triggers referral code generation (`generateReferralCode()`), sets initial `users` row via database trigger
- On login success: navigates to `/(auth)/plan-loading` if `onboarded === false`, or directly to `/(app)` if `onboarded === true`
- Writes to: `userStore` (sets user session state)

**Functional Constraints**:
- Loading state: After tapping "Create Account" / "Log In", the button shows a small activity spinner and text changes to "Creating account..." / "Logging in...". Button disabled during submission to prevent double-taps
- Empty state: N/A (form is always visible)
- Error state — Validation: Inline red error text below each invalid field after blur or submit. Error state — Auth: Full error banner below the form with danger background (10% opacity), danger text. Messages: "Email already in use", "Invalid login credentials", "Network error. Check your connection and try again." Each has a retry via tapping the button again
- Error state — Network: "Connection failed. Check your internet and try again." with the button re-enabled for retry. Persistent banner (doesn't auto-dismiss)
- Disabled state: Button disabled when any required field is empty or validation errors exist. During submission, all inputs are disabled
- Conditional visibility: Login mode hides the name input. Error banner shows/hides based on error state

---

#### 6. Plan Loading (`app/(auth)/plan-loading.tsx`)

**Purpose**: Display an engaging loading experience while Codex AI generates the user's personalised 90-day plan in the background.

**Core Components**:
- `MeshGradientBackground` — Animated mesh gradient (ember + teal blend at low opacity) for visual depth
- `GrainOverlay` — SVG noise texture at 4.5% opacity
- `AnimatedRingSpinner` — Centered animated SVG ring (teal stroke, 3px width, 64px diameter). Rotates continuously with a subtle dash-array animation (breathing effect). Duration: one full rotation per 2s
- `RotatingMessages` — Below the spinner: a text area that cycles through ~8 coaching messages every 2.5s. Messages fade in/out (500ms cross-fade). Text in body size (13px), bone color, centered, 280px max-width. Example messages: "Building your personalised plan...", "Analysing your goals and priorities...", "Selecting tasks from the Master Library...", "Calibrating to your face shape...", "Optimising your 90-day timeline...", "Crafting your pillar weights...", "Structuring your weekly rhythm...", "Almost ready..."
- `ProgressBar` — Thin bar below the messages (200px width, 2px height). Ember fill, muted track. Animates from 0% to ~90% over ~8s (simulated progress, not tied to actual generation progress). Final 10% snaps to 100% when generation completes
- `CancelLink` — Small text at the bottom: "Cancel" in caption size, muted. Taps cancel plan generation and navigate back to signup (aborts the in-flight Codex request)

**Information Architecture**:
- Calls: `planGenerator.generatePlan()` in `src/services/ai/planGenerator.ts` — sends quiz answers, Master Task Library context, and face shape weights to Codex AI via `callClaude()`
- Writes: Generated plan object to `planCache` (in-memory) for handoff to plan-reveal screen
- The Codex call is made with `model: "Codex-sonnet-4-6"`, system prompt from `src/services/ai/prompts/planPrompt.ts`
- Timeout: 30s for Codex response

**Functional Constraints**:
- Loading state: The entire screen IS the loading state — ring spinner + rotating messages + progress bar
- Empty state: N/A
- Error state — Timeout: If Codex takes >30s: "Plan generation is taking longer than expected. We're still working on it." The progress bar stays at ~90%. A "Wait" button appears (SecondaryButton) to extend the timeout by another 30s. After 60s total: "Something went wrong generating your plan." with two buttons: "Try Again" (ember PrimaryButton) and "Go Back" (SecondaryButton)
- Error state — API failure: "We couldn't generate your plan right now. Our AI might be temporarily unavailable." with "Try Again" button (retries the full generation) and "Go Back" (navigates to signup)
- Error state — Network: Same as API failure but with "Check your connection" messaging
- Disabled state: The cancel link is hidden during the first 3 seconds to prevent accidental cancellation. Buttons in error state are full-width and fully interactive
- Conditional visibility: Progress bar only appears after 1s (so it doesn't flash if generation is very fast). Cancel link hidden for first 3s

---

#### 7. Plan Reveal (`app/(auth)/plan-reveal.tsx`)

**Purpose**: Display the generated 90-day plan with estimated scores, focus areas, and an AI compliment before the user commits and enters the paywall.

**Core Components**:
- `MeshGradientBackground` — Subtle animated mesh gradient (teal tones) for premium feel
- `ScrollView` — Vertically scrollable content area with `Spacing.screen` horizontal padding
- `PlanHeroSection` — Top of scroll:
  - Program name: "Your 90-Day Transformation Plan" in title size (24px), bone, weight 700
  - Estimated score: hero size (64px), teal, with tight letter-spacing (-2.2), weight 700. Animated count-up
  - Subtext: "Estimated starting FORGE Score" in caption size, ash
- `FocusAreas` — Horizontal row (wrapping if needed) of pillar focus badges. Each badge: pillar color background at 15% opacity, pillar color text in caption size (11px), weight 700. Pill name + emphasis level (e.g. "Skin > High")
- `ExpectedImprovements` — Section with title "Expected Improvements" (heading size, 17px, bone). Below: list of 4–6 expected improvement items, each with: pillar color dot (8px), pillar name + improvement description in body size (13px), bone
- `DailyCommitment` — ForgeCard: "Daily Time Commitment" heading. Body text: "~15–30 minutes per day" in bone, "Across 2–5 tasks" in ash. Pill-shaped badge with time estimate
- `PhaseOverview` — Small card showing the 3 phases: Foundation (days 1–28), Activation (days 29–56), Optimisation (days 57–90). Each phase has its name from `PHASE_DISPLAY` (caption, weight 700, pillar color), range in small text, and a one-line description
- `AIComplimentCard` — Highlighted ForgeCard with ember border: "Your Starting Strength" heading. Below: 15–25 word AI-generated compliment about the user's strongest pillar from baseline analysis (e.g. "Your facial structure gives you a strong foundation. We'll build on that."). Body size (13px), bone text, italic style
- `PrimaryButton` — Fixed at bottom: "Start Transformation" (ember background, bone text, full-width with screen margins). On tap: saves plan to `plans` table, sets `onboarded=true`, sets `plan_start_date=now()`, navigates to paywall
- `SecondaryLink` — Below the button: "Not what you expected? Regenerate plan" in caption, muted. Tapping re-runs plan generation and returns to plan-loading

**Information Architecture**:
- Reads: Generated plan from `planCache` (populated by plan-loading)
- Reads: Quiz answers from `quizCache` for context
- Writes on confirm: Plan saved to Supabase `plans` table (`insertPlan()`), user updated with `onboarded=true` and `plan_start_date` via `updateUserOnboarding()`
- The plan data structure: `GeneratedPlan` type with `planName`, `pillarWeights`, `focusAreas`, `estimatedScore`, `dailyCommitmentMinutes`, `compliment`, `weeks[]`
- Writes to: `userStore` (updates onboarding state)

**Functional Constraints**:
- Loading state: If plan cache is empty (direct navigation to this screen without plan-loading), show full-screen message: "No plan found. Please go back and generate your plan." with a "Go Back" button
- Empty state: Same as loading — plan cache is required
- Error state — Save failure: If saving the plan to Supabase fails: "We couldn't save your plan. Tap to try again." with a "Try Again" PrimaryButton. After 3 failures: "Something isn't working. Please go back and try again later." with a "Go Back" SecondaryButton
- Error state — Network: "Connection lost while saving your plan. Check your internet and try again." with retry
- Disabled state: The "Start Transformation" button is briefly disabled (300ms) after the plan-reveal animation completes (score count-up) to prevent accidental immediate taps
- Conditional visibility: The "Regenerate plan" link only appears after 3s (so users don't immediately regenerate without reading). Phase overview shows only if the plan includes phase data

---

#### 8. Paywall (`app/(auth)/paywall.tsx`)

**Purpose**: Present the subscription offer and process payment via RevenueCat. Gate between onboarding and the main app.

**Core Components**:
- `PaywallBackground` — Dark canvas (`Colors.canvas`) background with subtle ember mesh gradient accent
- `PaywallHeader` — Top section:
  - FORGE wordmark: SpaceGrotesk-Bold, 32px display size, ember color, centered
  - Tagline: "Your 90-day transformation starts here" in caption size (11px), ash, centered, 200px max-width
- `FeatureList` — Vertically stacked checklist of features:
  - Each item: teal checkmark icon (16px) + bone text (body size, 13px), 8px gap
  - Features: "Personalised 90-day plan", "AI photo check-ins every 3 days", "Weekly coaching reports", "FORGE Score tracking across 9 pillars", "Progress heatmap and trend tracking", "XP, streaks, and achievements"
  - Items animate in with staggered fade (100ms delay each, from top to bottom)
- `PriceDisplay` — Below the feature list:
  - Price: "$11/mo" in hero size (64px), bone, weight 700, centered
  - Below: "Try 3 days free, then $11/mo. Cancel anytime." in caption size (11px), ash, centered, 240px max-width
  - Free trial emphasised with a subtle ember-colored pill badge: "3 DAYS FREE"
- `PrimaryButton` — Full-width ember button: "Start Free Trial". Calls RevenueCat `purchase()` for the Basic tier package
- `SecondaryButton` — Below the primary: "Restore Purchase" — outlined style (ember border, transparent background, bone text). Calls RevenueCat `restorePurchases()`
- `LegalLinks` — Row at the bottom: "Terms of Service" | "Privacy Policy" in caption size (11px), muted, separated by a dot. Each link opens the respective URL in the system browser
- `PaywallFooter` — Small text at very bottom: "FORGE Basic — $11/month. Auto-renews until cancelled." in 9px small size, muted, centered

**Information Architecture**:
- Calls: `RevenueCat.purchaseBasic()` — presents the native purchase sheet, returns purchase result
- Calls: `RevenueCat.restorePurchases()` — checks for existing purchases and restores entitlement
- Reads: `useSubscription` hook for current subscription status (to detect if already subscribed — then auto-redirect to app)
- Writes on success: Updates `users.subscription_tier` to `premium` via the `revenuecat-webhook` edge function (server-side). Updates `userStore` subscription state
- Post-purchase: Requests notification permissions (`expo-notifications`), schedules all 3 notification types via `notificationService.scheduleAll()`, navigates to `/(app)`
- Dev bypass: If `isDevBypass()` returns true (`__DEV__` and non-production env), mock purchase succeeds immediately without RevenueCat call

**Functional Constraints**:
- Loading state: After tapping "Start Free Trial", the button shows a spinner and "Processing..." text. The native iOS purchase sheet takes over during the RevenueCat purchase flow
- Loading state: "Restore Purchase" button shows spinner and "Restoring..." during restore
- Empty state: If RevenueCat offerings fail to load, a generic feature list and price are shown (hardcoded fallbacks)
- Error state — Purchase failed: "Purchase couldn't be completed. Please try again." with the primary button re-enabled. Specific messages: "Payment was cancelled" (user dismissed sheet), "Product not found", "Network error during purchase"
- Error state — Restore failed: "No previous purchase found. If you believe this is an error, contact support." in ash text below the button
- Error state — Already subscribed: If user is already subscribed (detected during load), auto-redirect to `/(app)` without showing the paywall
- Disabled state: Both buttons disabled during their respective operations (purchase/restore in-flight). Buttons show muted background and ash text
- Conditional visibility: The free trial badge only shows if RevenueCat's offering includes a trial. If no trial, button text changes to "Subscribe for $11/mo"

---

### (app)/(tabs) Group — Main App Tabs

#### 9. Home Tab (`app/(app)/(tabs)/index.tsx`)

**Purpose**: Primary daily dashboard showing the user's status, today's tasks, and AI coaching insight.

**Core Components**:
- `StatusStrip` — Top horizontal bar below safe area:
  - Streak badge: fire icon (ember, 16px) + streak count number (body size, bone, weight 700). Background: `Colors.raised`, 12px border radius, 12px horizontal padding, 8px vertical padding
  - FORGE Score: teal-colored number (heading size, 17px, weight 700) with "%" suffix in teal. "Score" label above it in small size, ash
  - Current phase: phase name from `PHASE_DISPLAY` in caption size (11px), pillar accent color, on the right
- `AITipCard` — ForgeCard with ember left border accent (3px):
  - AI icon (sparkle, ember, 16px) on the left
  - Insight text: body size (13px), bone, ≤25 words, italic style
  - Shimmer loading animation on the card when insight is being fetched
  - Swipe-to-dismiss (swipes right to dismiss, with spring animation back if incomplete)
- `TaskSection` — "Today's Tasks" heading (heading size, 17px, bone, weight 700) with task count badge (e.g. "3/5")
- `TaskCard` (2–5 instances) — Vertical list of task cards:
  - Each card: `Colors.surface` background, `Colors.divider` border (0.5px), 12px border radius, 16px padding
  - Left section: task title (outcomeTitle when day < 57, else clinical title) in body size (13px), bone. If completed: strikethrough, ash color, checkmark icon in teal
  - Right section: pillar badge (pillar color dot + short label in caption size), duration (min) in ash, XP value badge in ember
  - Chevron right icon (muted, 12px) for navigation to task detail
  - Ordering: incomplete tasks first (sorted by duration ascending), then completed tasks at bottom
  - Completion toggle: circular checkbox on the left (muted border when incomplete, teal fill + white check when complete). Tapping marks the task complete without navigating to detail
- `AllDoneCelebration` — When all tasks completed:
  - Animated checkmark (teal, 48px) with scale-in + bounce animation
  - "All Done for Today" in heading size, bone
  - "You earned X XP today" in body size, ash
  - Confetti-like particle animation (subtle, teal-colored dots)
- `RefreshControl` — Pull-to-refresh reloads tasks and insight. Ember-tinted spinner

**Information Architecture**:
- Reads from: `useTodaysTasks()` — returns today's tasks, completion count, total count
- Reads from: `useStreak()` — returns currentStreak, longestStreak
- Reads from: `useXP()` — returns totalXP, level, levelName
- Reads from: `useProgress()` — returns optimisationScore, programDay, pillarScores
- Reads from: `useCycles()` — returns latest cycle for phase context
- Calls on task complete: `completeTask(taskId)` from `useTasks` hook
- Daily insight fetched from: `generateDailyInsight()` in `coachingEngine.ts` via the `useDailyInsight` hook
- Writes on task complete: XP award via `xpService.awardXP()`, streak update via `streakService.updateStreak()`, pillar drift via `scoreCalculator.applyTaskEffect()`

**Functional Constraints**:
- Loading state: Skeleton cards — 3 gray placeholder rectangles with shimmer animation. Status strip shows placeholder values (dashed lines). AI insight card shows shimmer. Heatmap shows empty grid cells
- Empty state — No tasks: "No tasks for today. Check back tomorrow or review your progress." in body size, ash, centered. "View Progress" SecondaryButton below
- Empty state — First day (no history): The heatmap shows all "future" cells except today. First Strike modal triggers on the first task completion
- Error state — Task fetch failure: "Couldn't load your tasks. Pull down to retry." in body size, ash, centered. With a manual refresh icon button
- Error state — Insight fetch failure: The AI insight card shows a fallback static message: "Focus on today. Every task builds towards your transformation." in ash text. No shimmer. Non-dismissible
- Error state — Network offline: Banner at top of screen: "You're offline. Tasks will sync when you reconnect." in small size, muted, with warning icon
- Disabled state: Completed tasks show the completion toggle as filled teal but non-interactive (no tap response)
- Conditional visibility: The "All Done" celebration appears only when `completedCount === totalTasks` and at least one task was completed this session. AI insight card is visible always (with fallback). Status strip is always visible

---

#### 10. Progress Tab (`app/(app)/(tabs)/progress.tsx`)

**Purpose**: Display the user's FORGE Optimisation Score, per-pillar breakdown, XP level, and streak data.

**Core Components**:
- `ScoreHero` — Top section:
  - FORGE Optimisation Score in hero size (64px), teal, weight 700, centered, with tight letter-spacing. "+X" delta badge next to it (body size, success green if positive, danger red if negative, ash if zero). Animated count-up on load
  - "FORGE Score" label above the number in small size (9px), weight 700, ash, letter-spacing 1.8 (wide)
  - Score change indicator: "↑ +3 since last cycle" or "→ No change" or "↓ -2 since last cycle" in caption size (11px)
- `ScoreProgressRing` — Circular progress ring around the score (optional, 180px diameter). Teal arc fill proportional to score/100, muted track. Animated arc draw on load (1s)
- `GrainOverlay` — Subtle noise texture over the score area for depth
- `PillarBreakdownSection` — "Pillar Breakdown" heading (heading size, 17px, bone)
- `PillarScoreCard` (9 instances, visible 6 by default — `VISIBLE_PILLARS: skin, grooming, hair, posture, style, sleep`) — Grid (2 columns) or vertical list:
  - Each card: `Colors.surface` background, `Colors.divider` border, 12px border radius, 16px padding
  - Pillar name from `PILLAR_DISPLAY` in body size (13px), bone, weight 700
  - Score number in heading size (17px), pillar color, weight 700
  - Horizontal mini progress bar (pillar color fill, muted track, 4px height, full width)
  - Delta badge: "+X" in success, "-X" in danger, "—" in muted
  - "Show all 9 pillars" toggle at bottom expands to include facial_composition, nutrition, voice
- `XPLevelCard` — ForgeCard:
  - Current level name (e.g. "Adept") in heading size, ember, weight 700
  - Level progress bar: ember fill, muted track, 6px height. Shows "250 / 300 XP" in caption, ash
  - XP to next level: "50 XP to Level 4" in caption, ash
- `StreakCard` — ForgeCard:
  - Current streak: fire icon (ember) + streak count in heading size, bone
  - Longest streak: "Longest: 14 days" in caption, ash
  - Next milestone indicator: "7 days until 30-day milestone" with mini progress bar in ember
- `HeatmapSection` — "Your 90 Days" heading
- `HeatmapGrid` — 91-cell grid (days 1–90 + today):
  - Each cell: 10px square, 2px gap, 4px border radius
  - Status colors: `done` = teal (opaque), `partial` = teal (50% opacity), `missed` = surface (transparent with muted border), `future` = raised (empty)
  - Today's cell has an ember outline border (2px) to distinguish it
  - Below: legend row: "Done / Partial / Missed / Future" dots with labels in small size (9px), ash

**Information Architecture**:
- Reads from: `useProgress()` — optimisationScore, pillarScores (9), programDay, deltaVsBaseline
- Reads from: `useXP()` — totalXP, level, levelName, xpToNextLevel, leveledUp
- Reads from: `useStreak()` — currentStreak, longestStreak, isMilestone
- Reads from: `useHeatmap()` — cells[] with status per day
- Pillar scores are fetched from `progress` table (current snapshot) and `cycles` table (for delta calculation)
- All data refreshes on screen focus and pull-to-refresh

**Functional Constraints**:
- Loading state: Skeleton rectangles for the score hero (pulsing placeholder circle, 64px), skeleton cards for pillar scores (gray rectangles with shimmer), skeleton for heatmap (91 small gray squares)
- Empty state — New user (day 1–2, no cycles yet): Score shows the estimated score from onboarding with a "Estimated" label in caption, ash. Pillar section: "Complete your first cycle check-in on day 3 to see your scores" in body, ash, centered. Heatmap shows all future cells except today. Streak shows 0 with "Start your first task today" in ash
- Empty state — No heatmap data: "Your progress map will build over time. Complete tasks daily to fill it in." in body, ash
- Error state — Score fetch failure: "Couldn't load your scores. Pull down to refresh." with manual refresh button
- Error state — Pillar data failure: Individual pillar cards show "—" for score and "Unavailable" for delta, with a subtle warning icon. The card is still rendered but with reduced opacity
- Disabled state: N/A (read-only screen, no interactive state toggles)
- Conditional visibility: The "+X" delta badge only shows when there is a previous cycle to compare against (day > 3). "Show all 9 pillars" toggle only visible when the user has data for the hidden pillars. Streak card shows milestone progress bar only when within 7 days of the next milestone. XP level-up animation plays when `leveledUp` is true (from `useXP`)

---

#### 11. Program Tab (`app/(app)/(tabs)/program.tsx`)

**Purpose**: Show the full 90-day program structure, current week, and upcoming tasks to give users visibility into their transformation journey.

**Core Components**:
- `ProgramHeader` — Top section:
  - Current phase name from `PHASE_DISPLAY` in title size (24px), bone, weight 700
  - Phase tagline from `PHASE_DISPLAY` in caption, ash, italic
  - Phase range (e.g. "Days 29–56") in small size (9px), ash
- `PhaseProgressBar` — Horizontal bar (8px height, full-width with screen padding):
  - Three segments: Foundation (days 1–28), Activation (days 29–56), Optimisation (days 57–90)
  - Each segment colored by its phase accent (ember, teal, gold respectively at 30% opacity)
  - Current position indicator: white vertical line (2px) at the user's current day position. Animated position update
  - Labels below segments: phase names from `PHASE_DISPLAY` in small size (9px), ash
- `WeekTimeline` — Horizontally scrollable strip of week indicators:
  - 13 weeks (week 1–12 + optional week 13 for day 85–90). Each: numbered circle (32px), current week = ember fill + bone number, past weeks = teal fill + bone number, future weeks = muted outline
  - Tapping a week navigates to that week's detail (within the same tab, expands below)
  - Scrolls to current week on load (with offset animation)
- `CurrentWeekCard` — ForgeCard expanded for the current/selected week:
  - Week heading: "Week 4 of 13" in heading size, bone
  - Day list (7 rows): each row shows day number, day label (e.g. "Monday"), task count (e.g. "4 tasks"), completion indicator (checkmark if all done, partial circle if some done, empty circle if no tasks done)
  - Past days: muted opacity. Today: ember left border accent. Future days: ash text, no interaction
  - Tapping a day shows that day's task list in a bottom sheet or inline expansion
- `UpcomingMilestones` — ForgeCard:
  - "Coming Up" heading
  - List of upcoming milestones: next cycle check-in date, next weekly report, phase transition date, season end date
  - Each milestone: icon (camera for cycle, document for report, trophy for phase transition, star for season end), date in body size, description in caption

**Information Architecture**:
- Reads from: `useProgramStore` — the full `GeneratedPlan` with all weeks, days, and tasks
- Reads from: `useProgress()` — programDay for position tracking
- Reads from: `useCycles()` — upcoming cycle check-in dates
- The plan data is loaded once from Supabase `plans` table on app launch and cached in the Zustand store
- Week calculation: `currentWeek = Math.ceil(programDay / 7)`

**Functional Constraints**:
- Loading state: Skeleton for the phase progress bar (animated shimmer), skeleton week timeline (13 gray circles), skeleton current week card (gray rectangle)
- Empty state — No plan (edge case): "Your program plan isn't available. Please contact support." in body, ash, centered. With a "Contact Support" SecondaryButton
- Error state — Plan fetch failure: "Couldn't load your program. Pull down to refresh." with manual refresh
- Error state — Partial plan data: If weeks after the current week are missing (generation issue), show: "Rest of your program is being prepared. Check back soon." for future weeks
- Disabled state: Future weeks and days are visible but non-interactive (ash text, no tap response). Past days are tappable for review but tasks cannot be completed
- Conditional visibility: The phase milestone card only shows future milestones (hides past dates). Week timeline scroll indicator appears only when weeks exceed screen width

---

#### 12. Goals Tab (`app/(app)/(tabs)/goals.tsx`)

**Purpose**: Let users set, track, and manage personal goals and challenges alongside the structured program.

**Core Components**:
- `GoalsHeader` — "Your Goals" in title size (24px), bone, weight 700. Subtext: "Track your challenges and personal targets" in caption, ash
- `ActiveChallengesSection` — "Active Challenges" heading (heading size, 17px, bone)
- `ChallengeCard` (0–3 instances) — ForgeCard for each active challenge:
  - Challenge name in body size (13px), bone, weight 700
  - Progress bar: pillar color fill, muted track, 6px height. Shows "3/7 days" progress
  - Target: "7-day streak" or "Complete all posture tasks" in caption, ash
  - XP reward badge: "+50 XP" in ember, caption, weight 700
  - Visual treatment: ember border accent if near completion (≥80%)
- `BadgeCollection` — "Badges Earned" heading
- `BadgeGrid` — Grid of earned badges (3 columns):
  - Each badge: 56px circular icon with bronze/silver/gold metallic gradient background (hardcoded SVGs)
  - Badge name below in small size (9px), ash, centered, 1-line, width 72px, text-align center
  - Locked badges: grayed out with 0.3 opacity, lock icon overlay, "???" name
  - Tapping a badge shows a detail modal: badge name, description, date earned, celebration animation
- `PersonalGoalsSection` — "Personal Targets" heading
- `PersonalGoalCard` — Simple editable goal:
  - Goal text in body size, bone. Tapping lets user edit inline
  - "Add a personal goal" empty state card with plus icon and "Add a goal you want to track" in ash. Tapping opens a text input
  - Delete by swiping left (red background, trash icon)
- `MicroSprintPreview` — If a micro-sprint is upcoming or suggested:
  - ForgeCard with ember accent: "Suggested Sprint: Posture Focus"
  - "7 days, 3 posture tasks/day" in body, ash
  - "Accept Sprint" SecondaryButton in ember

**Information Architecture**:
- Reads from: `useChallenges()` — active challenges, completion status, progress
- Reads from: `useBadges()` — earned badges, locked badges, badge catalog from `src/constants/badges.ts`
- Reads from: `useSprints()` — available micro-sprints, active sprint
- Writes: Personal goals to user preferences/local storage (or Supabase `user_preferences` if available)
- Challenge progress synced to Supabase `challenge_progress` table
- Micro-sprints read from `src/constants/microSprints.ts` template library

**Functional Constraints**:
- Loading state: Skeleton cards for challenges (2–3 gray rectangles), badge grid skeleton (9 gray circles in 3×3), personal goals skeleton (1–2 gray lines)
- Empty state — No challenges: "No active challenges. Challenges unlock as you progress." in body, ash. "Browse Challenges" SecondaryButton
- Empty state — No badges: "No badges yet. Complete challenges and hit milestones to earn them." in body, ash. Show 3 locked badges as teasers
- Empty state — No personal goals: "Add a personal goal" card as the only item in the section
- Error state — Challenge fetch failure: Individual challenge cards show "Couldn't load" in muted text with a retry icon
- Error state — Badge fetch failure: Badge grid shows placeholder "—" states
- Disabled state: Locked badges are visible but non-interactive (no detail modal). Completed challenges show full progress bar but no interaction
- Conditional visibility: Micro-sprint preview card only appears when a sprint is suggested by the system or the user has an active sprint. Badge detail modal only opens for earned badges

---

#### 13. Sprints Tab (`app/(app)/(tabs)/sprints.tsx`)

**Purpose**: Browse, activate, and track micro-sprints — 7-day focused programs on a single pillar.

**Core Components**:
- `SprintsHeader` — "Sprints" in title size (24px), bone. Subtext: "7-day focus programs to boost a single pillar" in caption, ash
- `ActiveSprintBanner` — If a sprint is currently active:
  - Full-width ForgeCard with ember accent: sprint name, pillar badge, days remaining (e.g. "Day 3 of 7"), progress indicator
  - Tapping navigates to `sprint-detail` screen
- `SprintCatalog` — "Available Sprints" heading
- `SprintPreviewCard` (for each sprint template) — ForgeCard:
  - Sprint name in heading size (17px), bone
  - Target pillar badge (pillar color)
  - Description: 1–2 sentences in body, ash
  - Duration: "7 days" badge
  - Difficulty: "Beginner / Intermediate / Advanced" in caption, ash
  - XP reward: "+100 XP on completion" in ember, caption
  - "Start Sprint" SecondaryButton. On tap: confirms, replaces daily tasks with sprint tasks for 7 days, navigates to sprint detail
- `SprintHistoryCard` — If user has completed previous sprints:
  - "Past Sprints" heading
  - List of completed sprints: name, dates, pillar score change (e.g. "Posture: +4"), badge if all 7 days completed
  - Tapping shows sprint summary with before/after pillar score

**Information Architecture**:
- Reads from: `useSprints()` — active sprint, available templates, sprint history
- Reads from: `src/constants/microSprints.ts` — sprint template library
- Writes: Activating a sprint calls `sprintEngine.activateSprint()` which replaces the current week's tasks and updates `micro_sprints` table
- Sprint completion detection in `sprintEngine.checkCompletion()`
- Pillar score change calculated from cycle check-in data (pre-sprint vs post-sprint)

**Functional Constraints**:
- Loading state: Active sprint banner skeleton (gray rectangle), sprint catalog skeleton (3 gray cards with shimmer)
- Empty state — No sprints available: "No sprints available yet. Sprints unlock as you progress through your program." in body, ash
- Empty state — No sprint history: "Complete your first sprint to see it here." in body, ash, centered
- Error state — Sprint activation failure: "Couldn't start the sprint. Please try again." with the "Start Sprint" button re-enabled for retry
- Error state — Sprint data fetch failure: "Couldn't load sprints. Pull down to refresh."
- Disabled state: Sprint cards that require a higher level or program day show a lock icon overlay, muted colors, and "Unlocks at day 30" text. The "Start Sprint" button is replaced with the lock indicator
- Conditional visibility: Active sprint banner only shows when a sprint is active. Sprint history section only shows when `sprintHistory.length > 0`. Sprint availability depends on program day and user level

---

#### 14. Profile Tab (`app/(app)/(tabs)/profile.tsx`)

**Purpose**: Display user profile information, subscription status, app settings, and account management.

**Core Components**:
- `ProfileHeader` — Top section:
  - Avatar placeholder: 72px circle with user initials (bone text on raised background, weight 700, 24px). No photo upload currently
  - User name: heading size (17px), bone, weight 700
  - Member since: caption size, ash (e.g. "Member since March 2026")
- `PlanInfoCard` — ForgeCard:
  - Current season: "Season 1" in heading, ember
  - Program day: "Day 42 of 90" in body, bone
  - Current phase: phase name from `PHASE_DISPLAY` in caption, pillar accent
  - Plan type: "AI-Generated Personalised Plan" in caption, ash
- `SubscriptionCard` — ForgeCard:
  - Tier: "Basic — $11/month" in body, bone, weight 700
  - Status: "Active" pill badge (success green background at 15%, success text) or "Expired" (danger)
  - Renewal date: "Renews May 15, 2026" in caption, ash
  - "Manage Subscription" SecondaryButton — opens system subscription settings URL
- `SettingsSection` — "Settings" heading
- `SettingsRow` (multiple instances) — Simple tap rows:
  - Left: icon (16px, muted) + label (body, bone)
  - Right: chevron (12px, muted) or toggle switch (ember track when on, muted when off)
  - Settings: "Notifications" (toggle), "App Icon" (orchestrates native iOS alternate icons if implemented), "Privacy Policy" (opens URL), "Terms of Service" (opens URL)
- `DangerSection` — Separated section at the bottom:
  - "Sign Out" — Text row in danger color, body size, centered. On tap: calls `signOut()` from `useUserStore`, resets all Zustand stores, navigates to welcome
  - "Delete Account" — Text row in danger color, body size, centered, with warning icon. On tap: confirmation modal with "This permanently deletes all your data, photos, and progress." in body, bone. Two buttons: "Cancel" (SecondaryButton) and "Delete Forever" (danger background, bone text). On confirm: calls `deleteAccount()` which purges all user data from Supabase, deletes all photos from storage, signs out

**Information Architecture**:
- Reads from: `useUserStore` — user profile (name, email, onboarded, created_at, plan_start_date, season)
- Reads from: `useSubscription()` — isActive, expiresAt, tier
- Reads from: `useProgress()` — programDay for plan info
- Writes: Sign out calls `supabase.auth.signOut()` and resets all stores. Notification preferences saved to user preferences
- Delete account calls a Supabase edge function (`delete-account`) that cascades deletions across all tables and storage

**Functional Constraints**:
- Loading state: Skeleton for profile header (gray circle + gray lines), skeleton for plan info card, skeleton for subscription card
- Empty state: N/A (profile data is hydrated from user store, which is populated on auth)
- Error state — Subscription fetch failure: Subscription card shows "Unable to load subscription info. Pull down to refresh." with a retry icon
- Error state — Sign out failure: "Sign out failed. Please try again." with retry. Falls back to clearing local state and navigating to welcome even if server sign-out fails
- Error state — Delete account failure: "Account deletion failed. Please try again or contact support." with "Try Again" and "Contact Support" buttons
- Disabled state: Delete account confirmation has both buttons. The "Delete Forever" button shows a 3-second countdown before it becomes tappable to prevent accidental taps ("Delete Forever (3)", "(2)", "(1)"). During the countdown, the button is disabled (muted background)
- Conditional visibility: Subscription management button only shows when subscription is active. Plan info card only shows after onboarding is complete

---

### (app) Group — Modal & Detail Screens

#### 15. Cycle Check-In (`app/(app)/cycle.tsx`)

**Purpose**: Capture progress photos every 3 days, run AI analysis, and display results.

**Core Components**:
- `CycleScreen` — Full-screen camera-first experience
- `FaceGuideOverlay` — Semi-transparent overlay with a white elliptical outline indicating face positioning. Center of screen. "Position your face within the guide" in caption, ash, below the guide outline
- `CameraViewfinder` — `expo-camera` CameraView filling the screen. Front-facing camera by default. Camera controls: flash toggle (top-right), flip camera (bottom-right), capture button (bottom-center, large circle: 72px diameter, white border 4px, inner circle 60px, white at 70% opacity. Animates scale to 0.9 on press)
- `ScanModeSelector` — Top-left: "Face" / "Full" segmented toggle. Face mode = front photo only (style/sleep/nutrition/voice set to data_gap). Full mode = requires left + right + front photos (all pillars analysed). Currently "Full" mode is available but Face mode is the default and primary mode
- `PhotoReview` — After capture: shows the photo full-screen with two buttons: "Retake" (SecondaryButton, left) and "Use Photo" (PrimaryButton, ember, right)
- `UploadingOverlay` — Full-screen overlay with spinner and "Uploading & analysing..." text in body, bone. Shows upload progress (photo upload) then analysis progress (AI processing). Two-step progress bar (2 segments: upload + analyse)
- `CycleResultCard` — Post-analysis results:
  - FORGE Score: hero size (64px), teal, with "+X" delta badge
  - Cycle number: "Cycle 4" badge in ember, caption
  - Pillar score bars (6 visible pillars for face mode): horizontal bars with pillar color fill, score number in bone, delta badge
  - "All 9 Pillars" toggle expands to show hidden pillars with "Data Gap" labels in muted
  - AI Insight: ForgeCard with insight text in body, bone, italic. "What this means" in small label, ash
  - Next Focus: ember-accented card: "Focus on: Posture" with 1-sentence coaching direction
  - Photo thumbnail with face shape label ("Oval", "Square", etc.)
- `HistoryAccess` — "View All Check-Ins" SecondaryButton at bottom. Navigates to photo-timeline

**Information Architecture**:
- Reads from: `useCycles()` — daysUntilNextCycle, canCheckInNow, latest cycle
- Reads from: `useProgress()` — current pillar scores for delta context, face shape
- Calls: `imageService.capture()` or `imageService.pick()`, then `imageService.compress()`, then `imageService.upload()`, then `getSignedPhotoUrl()`
- Calls: `photoAnalyser.analyseCycle()` via `callClaudeVision()` with the signed URL, scan mode, previous scores, face shape
- Writes: Cycle result to `cycles` table. Updates `progress` table with new pillar scores
- Gate: If no baseline photo exists, redirect to `baseline-photo` screen first with a message: "You need a baseline photo before your first check-in."

**Functional Constraints**:
- Loading state: The uploading overlay IS the loading state — two-step progress indicator
- Empty state — Not a check-in day: If `canCheckInNow === false`: "Next check-in in X days" in heading, bone, centered. "Your next cycle photo is on [date]. Check back then." in body, ash. "View Past Check-Ins" SecondaryButton
- Empty state — No cycles yet: "Your first cycle check-in unlocks on day 3. Take your baseline photo first." in body, ash
- Error state — Camera permissions denied: "Camera access is required for cycle check-ins. Enable it in Settings." with "Open Settings" PrimaryButton
- Error state — Photo upload failed: "Upload failed. Check your connection and try again." with "Try Again" and "Skip for Now" buttons
- Error state — AI analysis failed: "Analysis couldn't be completed. Our AI might be temporarily unavailable." with "Try Again" button that re-sends the photo (no re-upload needed — signed URL already exists)
- Error state — Network offline during upload: "You're offline. Photos can't be uploaded without a connection." with "Retry When Online" button. Queue the upload for retry
- Disabled state: Capture button disabled during upload/analysis. "Full" scan mode may be disabled (grayed out) for users on free trial or day < 14
- Conditional visibility: Face guide overlay only visible during camera preview (not during review or results). Scan mode selector hidden during upload and results. Photo review only shown after capture

---

#### 16. Baseline Photo (`app/(app)/baseline-photo.tsx`)

**Purpose**: Capture the user's first photo required as a reference point for all future cycle check-ins and score calculations.

**Core Components**:
- `BaselineScreen` — Full-screen camera viewfinder with face guide overlay (same as cycle screen)
- `BaselineHeader` — Top section (over camera):
  - "Baseline Photo" in title size (24px), bone, centered
  - "Your starting point. Same angle, same lighting." in caption, ash, centered
  - Back/X button top-left to dismiss (if optional) — but baseline is effectively required before first cycle
- `FaceGuideOverlay` — Same elliptical guide as cycle screen. "Position your face within the guide"
- `CaptureButton` — Same large circle button as cycle screen
- `PhotoReview` — After capture: "This is your starting point. Make sure the lighting is good." in body, ash, centered. "Retake" / "Use Photo" buttons
- `UploadingOverlay` — Same as cycle screen but with "Setting your baseline..." messaging
- `BaselineResultCard` — Post-analysis:
  - "Baseline Set" in heading, bone, weight 700, with checkmark icon (success green)
  - Initial FORGE Score estimate in teal, heading size
  - Face shape detection: "Face Shape: Oval" in body, bone, with face shape diagram
  - Onboarding compliment: AI-generated 15–25 word strength callout. "Your strongest asset" label in small, ash. Compliment text in body, bone, italic
  - "Continue" PrimaryButton (ember) — updates `users.baseline_photo_url`, `users.baseline_photo_path`, `users.face_shape`, dismisses screen
- `GrainOverlay` — Subtle SVG noise texture during the result card

**Information Architecture**:
- Reads from: `useProgress()` — checks if baseline already exists (if yes, show a message instead)
- Reads from: `useCycles()` — no cycles yet, will unlock after baseline
- Calls: Same image capture, compress, upload, signed URL pipeline as cycle check-in
- Calls: `callClaudeVision()` with baseline-specific prompt (initial score estimation + face shape detection + onboarding compliment)
- Writes: `users.baseline_photo_url`, `users.baseline_photo_path`, `users.face_shape`. Also writes initial pillar scores to `progress` table
- The `(auth)/baseline-photo.tsx` variant is kept for edge cases during onboarding recovery

**Functional Constraints**:
- Loading state: Upload overlay with "Setting your baseline..." + spinner + progress steps
- Empty state: N/A (camera is the main content)
- Error state — Camera permissions: Same as cycle screen
- Error state — Baseline already exists: "You already have a baseline photo. View it in your progress." with "View Progress" PrimaryButton. Optionally: "Take New Baseline" SecondaryButton (warning: "This will reset your scores")
- Error state — Upload/Analysis failure: Same error patterns as cycle screen
- Error state — AI analysis failure: "We couldn't analyse your photo right now. You can continue without a baseline, but you'll need one before your first cycle check-in." with "Skip for Now" (sets a `baseline_pending` flag) and "Try Again" buttons
- Disabled state: Capture button disabled during upload/analysis
- Conditional visibility: The "Continue" button is disabled (500ms) during result animation. "Take New Baseline" only visible if baseline already exists

---

#### 17. Photo Compare (`app/(app)/photo-compare.tsx`)

**Purpose**: Visually compare two cycle photos side-by-side to see progress over time.

**Core Components**:
- `CompareHeader` — "Compare Photos" in title size (24px), bone. "Slide to compare your progress" in caption, ash
- `DualPhotoViewer` — Two large photo panels side-by-side with 8px divider gap:
  - Left panel: "Before" label (small, weight 700, ash) above. Photo from the selected earlier cycle. Shows cycle number and date
  - Right panel: "After" label above. Photo from the selected later cycle. Shows cycle number and date
  - Photo fills the container with `resizeMode: "cover"`, 4px border radius
- `SliderOverlay` — A vertical draggable divider line (2px width, white at 50% opacity) that reveals more of the "before" or "after" photo. Drag handle: 24px circle with arrow icons. Default position: center
- `CycleSelectors` — Two rows of pill-shaped selectors (horizontally scrollable):
  - Top row: "Before: Cycle 1 / Cycle 2 / Cycle 3 / Baseline" — each as a pill button (raised background, bone text when unselected, ember background + bone text when selected)
  - Bottom row: "After: Cycle 2 / Cycle 3 / Cycle 4 / Latest" — same style
  - Selected state: ember fill + bone text. Unselected: raised background + ash text
- `ScoreDeltaSummary` — ForgeCard below the photos:
  - Per-pillar comparison: "Skin: Before 42 → After 58 (+16)", each row with pillar color, bone text
  - Overall FORGE Score delta: "+12" in teal, heading size
- `PrimaryButton` — At bottom: "Share Comparison" (ember). Uses `useShareCard` to generate a comparison share card via `react-native-view-shot`

**Information Architecture**:
- Reads from: `useCycles()` — cycle history for photo URLs and scores
- Reads from: `useProgress()` — current scores for latest comparison
- The photos use signed URLs generated by `getSignedPhotoUrl()` — these may need regeneration if the default 3600s has expired
- Score deltas calculated client-side from the two selected cycles' pillar scores

**Functional Constraints**:
- Loading state: Skeleton photo panels (gray rectangles with shimmer). Skeleton score delta card (gray lines with shimmer)
- Empty state — Only one photo: "You need at least 2 check-ins to compare. Your next cycle is in X days." in body, ash, centered. "View Photo Timeline" SecondaryButton
- Empty state — No photos: "No photos to compare yet. Complete your first cycle check-in." in body, ash. "Go to Check-In" PrimaryButton
- Error state — Signed URL expired: "Photo unavailable. Tap to reload." with retry icon. Re-generates signed URL on tap
- Error state — Score data missing: Individual pillar rows show "—" for unavailable scores
- Disabled state: The slider overlay is disabled during photo loading. Cycle selectors disable options that don't have photos
- Conditional visibility: Score delta card only shows when both selected cycles have score data. Share button only visible when comparison is valid. Slider overlay only visible when both photos are loaded

---

#### 18. Photo Timeline (`app/(app)/photo-timeline.tsx`)

**Purpose**: Browse the user's complete cycle check-in history in chronological order.

**Core Components**:
- `TimelineHeader` — "Photo Timeline" in title size (24px), bone. "Your transformation in photos" in caption, ash
- `TimelineList` — Vertically scrollable list of photo cards in reverse-chronological order (newest at top):
  - Each `TimelineCard`: `Colors.surface` background, `Colors.divider` border, 12px border radius
  - Left: photo thumbnail (80px × 107px, 3:4 aspect ratio, `resizeMode: cover`, 8px border radius). If photo is unavailable, show a gray placeholder with camera icon
  - Right section: Cycle number badge ("Cycle 4" in ember, caption, weight 700), date (body, bone), FORGE Score (heading, teal), primary insight snippet (1 line, caption, ash, truncated)
  - Chevron right icon for navigation to cycle detail
  - Tapping navigates to cycle result view (expanded card or detail screen)
- `TimelineStats` — Top summary card (ForgeCard):
  - Total check-ins: "8 check-ins" in heading, bone
  - First check-in date
  - Latest check-in date
  - Average score improvement per cycle: e.g. "+2.3 per check-in" in teal
- `BaselineCard` — If baseline photo exists, a special card at the very bottom:
  - "Your Starting Point" label with "Baseline Photo" in body, bone
  - Photo thumbnail with "Day 3" badge
  - Face shape detection result
  - "This is where it all began." in caption, ash, italic
- `TimelineConnector` — Vertical line (2px width, `Colors.divider`, animated draw on scroll) connecting all cards on the left side, creating a visual timeline effect

**Information Architecture**:
- Reads from: `useCycles()` — cycle history array with all photos, scores, and insights
- Reads from: `useProgress()` — baseline photo URL and face shape
- Signed URLs may need regeneration for older photos
- Cycles ordered by `cycle_number` descending (newest first)

**Functional Constraints**:
- Loading state: Skeleton timeline: 4–5 gray cards with shimmer animation (photo thumbnail placeholder + text line placeholders)
- Empty state — No cycles: "No check-ins yet. Your first cycle photo unlocks on day 3. Take your baseline photo to get started." in body, ash, centered. "Take Baseline Photo" PrimaryButton (if no baseline) or "First Check-In in X days" message
- Empty state — Baseline exists but no cycles: "Your baseline is set. Your first cycle check-in unlocks on day 6." with days countdown and "View Baseline" SecondaryButton
- Error state — Photo load failure on individual cards: The thumbnail shows a gray placeholder with a broken image icon. The rest of the card data (score, date, insight) still renders. "Tap to reload" on the thumbnail
- Error state — Full timeline fetch failure: "Couldn't load your photo timeline. Pull down to refresh."
- Disabled state: N/A (read-only screen)
- Conditional visibility: Timeline stats card only shows when ≥1 cycle exists. Baseline card only shows at the bottom when `baseline_photo_url` is set. Timeline vertical connector only shows when ≥2 cards exist

---

#### 19. Share Card (`app/(app)/share-card.tsx`)

**Purpose**: Generate and preview a shareable FORGE progress card, then share via the native iOS share sheet.

**Core Components**:
- `ShareCardPreview` — A visual card rendered for screen capture (`react-native-view-shot`):
  - Background: `Colors.canvas` with subtle ember mesh gradient accent
  - FORGE wordmark at top (SpaceGrotesk-Bold, 20px, ember)
  - Card type label: "FORGE Score" / "Streak Milestone" / "Season Complete" / "Before & After" in small size (9px), ash, weight 700, letter-spacing 1.8 (wide)
  - Main metric: FORGE Score in hero size (64px), teal, centered, or streak number with fire icon, or before/after score comparison
  - Pillar highlight: 1–3 top pillars with scores in pillar colors, caption size
  - User's program day and level: "Day 42 · Level 3 — Adept" in caption, ash
  - FORGE tagline at bottom: "Built by FORGE — 90-day appearance transformation" in small size (9px), muted
  - All text uses Inter or SpaceGrotesk as appropriate. No emojis (ShareCard is rendered to image)
  - Export dimensions: 1080 × 1080 (square, Instagram-optimised), or 1080 × 1920 (story, vertical)
- `ShareTypeSelector` — Horizontal row of pill tabs: "FORGE Score" / "Streak" / "Before & After" / "Season Complete". Selected: ember fill + bone text. Unselected: raised background + ash text
- `AspectToggle` — Segmented control: "Square / Story". Changes the preview card dimensions
- `OverlayBadge` (optional, for "Before & After" type) — Semi-transparent overlay on the progress photo with score overlay text
- `PrimaryButton` — At bottom: "Share" (ember). On tap: captures the preview area via `react-native-view-shot`, then opens the native iOS share sheet with the image
- `SecondaryLink` — "Not ready to share? View in app" in caption, muted. Dismisses the share screen

**Information Architecture**:
- Reads from: `useShareCard()` — generates share card data based on type selector
- Reads from: `useProgress()` — optimisationScore, pillarScores, programDay
- Reads from: `useStreak()` — currentStreak for streak cards
- Reads from: `useCycles()` — before/after photos and scores for comparison cards
- Uses: `shareService.generateShareCard()` to compose the card data
- Uses: `react-native-view-shot` `captureRef()` for image capture
- Uses: `expo-sharing` or `Share` API for the native share sheet

**Functional Constraints**:
- Loading state: Share card preview shows a pulsing skeleton of the card layout while data loads. Share button disabled with "Loading..." text
- Empty state — Share type unavailable: "This share type requires more data. Complete a few more days to unlock it." (e.g., streak card requires streak > 3, before/after requires ≥2 cycles)
- Error state — Image capture failed: "Couldn't generate the share image. Please try again." with "Retry" button
- Error state — Share sheet failed: "Sharing was cancelled or failed. You can try again." (this is not really an error — share sheets can be dismissed)
- Error state — Data missing for selected type: "Not enough data for this share type yet. Keep progressing!" in body, ash
- Disabled state: The share button is disabled during image capture (shows "Preparing..." with spinner). Share type tabs disable when the user doesn't have enough data for that type
- Conditional visibility: Share type tabs only show available types (hide "Before & After" if only 1 cycle). Aspect toggle always visible. The "Share" button is always visible but may be in disabled state during capture

---

#### 20. Season Complete (`app/(app)/season-complete.tsx`)

**Purpose**: Celebrate the completion of a 90-day Season with an animated score reveal, narrative report, and season rollover.

**Core Components**:
- `CelebrationAnimation` — Full-screen animated background:
  - Mesh gradient transitions through ember, teal, gold tones over 3s
  - Confetti-like particles (subtle, teal and ember dots) animating upward and outward
  - Scale-pulse on the FORGE wordmark
- `SeasonHero` — Top section:
  - "Season 1 Complete" in SpaceGrotesk-Bold, 32px display size, bone, centered. Fade-in + scale-up animation
  - Before/After score comparison: Starting score on left (muted, 24px, ash) with "Day 1" label. Arrow → in ember. Final score on right (hero 64px, teal, weight 700) with "Day 90" label. Animated count-up on the final score
  - Delta badge: "+X" in teal, heading size, with pill background (teal at 15%)
- `SeasonReport` — Scrollable ForgeCard with the full AI-generated season report:
  - "Your Season 1 Story" heading (heading size, 17px, bone)
  - Narrative report text: 400–600 words in markdown-rendered format. Bone headings, ash body. Uses MECHANISM language stage
  - Sections: Starting Point, Breakthrough Moments (largest pillar movers), Habits That Stuck, Areas That Plateaued, and Focus for Season 2
  - Each pillar mentioned has its pillar color accent badge inline
- `PillarMovementSummary` — ForgeCard:
  - Table/list of all 9 pillars: pillar name, starting score (muted), ending score (bone), delta (teal if positive, danger if negative, ash if zero). Sorted by delta descending (biggest movers first)
  - Mini sparkline bars showing the trend over the season (horizontal, pillar color)
- `AchievementsEarned` — ForgeCard:
  - Badges earned during Season 1: icon + name + date earned
  - "View All Badges" link
- `PrimaryButton` — Fixed at bottom: "Start Season 2" (ember). On tap: triggers season rollover, generates new plan, navigates to plan-reveal for Season 2
- `SecondaryButton` — Above the primary: "Share Season Results" (ember border, bone text)
- `SeasonReportFooter` — Small text at very bottom: "Your data is saved. Season 2 will build on everything you've achieved." in caption, ash, centered

**Information Architecture**:
- Reads from: `useProgress()` — optimisationScore (final), programDay (should be 90)
- Reads from: `useCycles()` — cycle history for pillar trend data and before/after photos
- Calls: `coachingEngine.generateSeasonReport()` — generates the 400–600 word narrative
- Calls: `challengeEngine.getSeasonAchievements()` — badges earned this season
- Writes on rollover: Updates `users.season` to 2, `users.program_day` to 1. Generates new plan via `planGenerator.generatePlan()` with updated weights incorporating cycle data. Clears and repopulates `daily_tasks`
- Records season completion event in `season_events` audit table

**Functional Constraints**:
- Loading state: While the season report is being generated (AI call), show a "Crafting your season story..." screen with animated ring spinner, similar to the plan-loading screen. The score comparison is displayed immediately (client-side data)
- Empty state — Report generation still in progress: "Your season story is being written. This takes a moment." with spinner
- Error state — Report generation failed: "We couldn't generate your full season report right now. Your scores are safe." with "View Scores" PrimaryButton to see the pillar movement summary without the narrative, and "Retry Report" SecondaryButton
- Error state — Season rollover failed: "Season 2 setup couldn't be completed. Your Season 1 data is preserved. Try again or contact support." with "Try Again" and "Contact Support" buttons
- Disabled state: "Start Season 2" button is disabled (500ms) during celebration animation. During season rollover (plan generation), the button shows "Setting up Season 2..." with spinner
- Conditional visibility: The "Share Season Results" button only shows when user has opted into sharing. Achievements section only shows if the user earned badges. The celebration animation only plays once (tracked via local state flag)

---

#### 21. Task Detail (`app/(app)/task/[taskId].tsx`)

**Purpose**: Show detailed information about a single daily task including the "why it works" explanation, and provide the completion action.

**Core Components**:
- `TaskDetailHeader` — Top section:
  - Task title: heading size (17px), bone, weight 700. If task uses `outcomeTitle`, display that (when day < 57). If day ≥ 57, display the clinical title
  - Back arrow top-left
- `PillarBadge` — Pill label in full pillar color background (15% opacity), pillar color text, body size, weight 700. Pill name from `PILLAR_DISPLAY`
- `MetaRow` — Horizontal row of meta info badges:
  - Duration: clock icon (12px, muted) + "X min" in caption, ash
  - XP: star icon (12px, ember) + "+X XP" in caption, ember, weight 700
  - Frequency: calendar icon + "Daily" in caption, ash
- `WhyItWorksCard` — ForgeCard:
  - "Why It Works" heading (body size, 13px, bone, weight 700)
  - Explanation text in body size (13px), bone, with 1.55 line height. Format: 2–4 sentences explaining the science or logic behind the task
  - Expanded by default when day ≥ 29 (`showWhyByDefault(day)`)
  - Decorative element: pillar color left border accent (3px) on the card
- `RelatedTasksCard` — ForgeCard (optional, if related task data available):
  - "Related Tasks" heading
  - 2–3 related task previews: title + pillar badge, tapping navigates to their detail
- `TaskNotesCard` — ForgeCard (optional):
  - "Your Notes" heading with "Add Note" SecondaryLink
  - User's personal notes about this task type. Empty state: "Add notes about this task" in ash, caption
- `CompleteButton` — Fixed at bottom:
  - If task is incomplete: ember PrimaryButton: "Mark Complete". Shows XP badge next to it (e.g. "+10 XP" or "+30 XP with streak bonus")
  - If task is completed: success state — green checkmark icon (24px) + "Completed at 10:42 AM" in caption, ash. Button background changes to surface (non-interactive)
  - Completion animation: button shrinks to a checkmark circle, then expands back (300ms spring)

**Information Architecture**:
- Reads from: `useTasks()` — fetches individual task by `taskId` from `daily_tasks` table
- Reads from: `useStreak()` — current streak to calculate XP bonus for the completion button text
- Reads from: `useProgress()` — programDay for language stage and `showWhyByDefault` logic
- Writes on complete: `completeTask(taskId)` — marks task complete in `daily_tasks`, awards XP, updates streak, applies pillar drift (+0.5), queues pending effect if offline
- Task data includes: `title`, `outcomeTitle`, `pillar`, `tier`, `xpValue`, `duration_mins`, `whyItWorks`, `whyShort`, `libraryTaskId`

**Functional Constraints**:
- Loading state: Skeleton card for the task title (gray rectangle, 2 lines), skeleton for meta badges (3 small gray pills), skeleton for why-it-works card (3 gray lines)
- Empty state — Task not found: "Task not found. It may have been removed or the day has passed." in body, ash, centered. "Go Back" SecondaryButton
- Error state — Task fetch failure: "Couldn't load task details. Tap to retry." with retry icon
- Error state — Completion failed: "Marking complete failed. Check your connection and try again." — the button reverts to its uncompleted state. The task is NOT marked complete locally (waits for server confirmation)
- Disabled state: Completed tasks show the completion state — green checkmark, no button interaction. Future tasks (day > programDay) show the task details but the completion button is hidden or replaced with "Unavailable until [date]" in muted text
- Conditional visibility: "Why It Works" is always visible but may be collapsed (accordion style) for days < 29. Related tasks section only appears if the task has related tasks defined in the task library. Notes section always appears but may be empty. The streak bonus text on the completion button only shows when `streak > 3`

---

#### 22. Pillar Detail (`app/(app)/pillar/[pillar].tsx`)

**Purpose**: Deep-dive into a single pillar's score, trend, contributing tasks, and coaching context.

**Core Components**:
- `PillarHeader` — Top section:
  - Pillar name from `PILLAR_DISPLAY` in title size (24px), pillar color, weight 700
  - Back arrow top-left
  - Pillar tagline (e.g. "Clarity" for skin, "Frame" for posture) in caption, ash, italic — the "brand" name from `PILLAR_DISPLAY` when season ≥ 2, otherwise the plain name
- `PillarScoreHero` — Large score display:
  - Current score in hero size (64px), pillar color (not teal — each pillar has its own color), weight 700
  - Score ring: circular progress (180px diameter, pillar color arc fill, muted track)
  - Delta: "+X since last cycle" or "—" below the score
  - Score change indicator: arrow up (success) or arrow down (danger) in body size
- `PillarTrendGraph` — ForgeCard:
  - "Score Trend" heading (body, bone, weight 700)
  - Simple line or bar chart showing the pillar score across all cycles (cycle 1, 2, 3... N on X-axis, score 0–100 on Y-axis). Line color: pillar color. Fill area below the line: pillar color at 10% opacity
  - If only 1 data point: "More check-ins needed to show your trend." in caption, ash
- `ContributingTasks` — ForgeCard:
  - "Tasks That Improve This Pillar" heading
  - List of 3–5 tasks from the user's plan that affect this pillar. Each: task title with completion checkmark if done in the past, pillar badge, "Completed X times" in caption, ash
  - Tapping a task navigates to its task detail
- `PillarCoachingCard` — ForgeCard:
  - AI-generated coaching specific to this pillar (if available from the latest cycle analysis or weekly report)
  - "Coaching Note" label in small size, ash. Insight text in body, bone
  - If no coaching data: "Complete your next cycle check-in for personalised pillar coaching." in caption, ash
- `PillarWeightCard` — ForgeCard:
  - "Your Weight: X%" — shows this pillar's contribution to the FORGE Optimisation Score
  - Weight bar: pillar color fill proportional to the weight, muted track
  - "This pillar contributes X% to your overall FORGE Score." in caption, ash

**Information Architecture**:
- Reads from: `useProgress()` — pillar score, pillar weight, delta
- Reads from: `useCycles()` — cycle history for trend graph data points
- Reads from: `useTasks()` — tasks filtered by pillar for the contributing tasks section
- The `pillar` route parameter determines which pillar to display: `facial_composition`, `skin`, `grooming`, `hair`, `posture`, `style`, `sleep`, `nutrition`, `voice`
- Pillar color from `Colors.*` (e.g., `Colors.skin`, `Colors.style`)

**Functional Constraints**:
- Loading state: Skeleton for score hero (circle + number placeholder), skeleton cards for trend graph (gray rectangle), contributing tasks (2–3 gray lines), coaching card
- Empty state — No score data: "No score data for [pillar] yet. This pillar's score is calculated from your cycle check-in photos." in body, ash. If the pillar is excluded from the current scan mode (e.g., voice in face mode): "This pillar requires Full scan mode for analysis." in body, ash
- Empty state — No trend data: The trend card shows "More check-ins needed to show your trend. Keep going!" with just the current score dot plotted
- Empty state — No contributing tasks: "You don't have any [pillar] tasks in your current plan." in caption, ash
- Error state — Score fetch failure: "Couldn't load [pillar] data. Pull down to refresh."
- Error state — Invalid pillar: If the route parameter doesn't match a valid pillar ID: "Pillar not found. Go back and try again." with "Go Back" SecondaryButton
- Disabled state: N/A (read-only screen)
- Conditional visibility: The trend graph only renders when ≥2 data points exist. Pillar coaching card content depends on whether the latest cycle included coaching for this pillar. Weight card always visible

---

#### 23. Weekly Report (`app/(app)/weekly-report/[week].tsx`)

**Purpose**: Display an AI-generated weekly coaching report with pillar movement analysis, coaching notes, and next week's focus.

**Core Components**:
- `ReportHeader` — Top section:
  - "Week X Report" in title size (24px), bone, weight 700
  - Date range below: "Mar 15 – Mar 21, 2026" in caption, ash
  - Back arrow top-left
  - Week selector: left/right arrow buttons to navigate between weeks. "Week 4 of 12" indicator in caption, ash, centered
- `OverallScoreCard` — ForgeCard:
  - This week's average score or end-of-week score in heading size (17px), teal, weight 700
  - Delta from previous week: "+X" or "—" or "-X" with appropriate color
  - Mini sparkline of daily scores (if available)
- `PillarMovementSection` — "Pillar Movement" heading
- `PillarMovementRow` (9 instances) — Each row:
  - Pillar name from `PILLAR_DISPLAY` in body, bone
  - This week's score in body, bone
  - Delta arrow: ↑ in success, ↓ in danger, → in muted
  - "Biggest Mover" badge (ember pill) on the pillar with the largest absolute delta
- `CoachingNarrative` — ForgeCard (main content):
  - The AI-generated report text: 180–250 words in markdown format
  - Rendered sections: habit adherence (what stuck), breakthrough moments (largest improvement), friction points (pillars that struggled), and next week's focus
  - Bone text for headings, ash text for body. Language stage appropriate to the program day
- `TaskCompletionCard` — ForgeCard:
  - Completion rate: "5/7 days completed" with visual bar (teal fill for completed days, muted for missed)
  - Average tasks per day: e.g. "3.2 tasks/day"
  - Total XP earned this week: "+180 XP" in ember
- `NextWeekPreview` — ForgeCard:
  - "Next Week's Focus" heading
  - Pillar to focus on (from the report): pillar badge + 1-sentence direction
  - Upcoming cycle check-in date
  - Milestone alert: "30-day streak milestone in 3 days!" if applicable
- `ShareButton` — SecondaryButton: "Share Report" (if implemented). Generates a weekly report share card
- `WeekNavigator` — Bottom bar with previous/next week arrows and a "Latest" button that jumps to the most recent report

**Information Architecture**:
- Reads from: `useWeeklyReports()` — weekly report data from the `weekly_reports` table for the specified week number
- Reads from: `useProgress()` — programDay for context
- Reads from: `useTasks()` — completion data for the task completion card
- The `week` route parameter determines which week's report to display
- Reports are generated by the `weekly-report-generator` edge function (cron: Sunday 06:00 UTC) and stored in `weekly_reports`
- If the report for the requested week hasn't been generated yet (future week or generation in progress), show appropriate state

**Functional Constraints**:
- Loading state: Skeleton for report header, skeleton cards for score, pillar movement (9 skeleton rows), coaching narrative (5–6 gray lines), task completion (gray bar)
- Empty state — Report not yet generated: "Your Week X report is being prepared. Reports are generated every Sunday." in body, ash, centered. In dev: "This report hasn't been generated yet. Complete the week to trigger it." with estimated generation time
- Empty state — No reports at all: "Weekly reports start after your first full week. Complete your daily tasks to unlock your first report." in body, ash, centered
- Empty state — Week number out of range: "Week X is outside your program. Your program runs for 12 weeks." with a link back to the latest available report
- Error state — Report fetch failure: "Couldn't load the Week X report. Pull down to refresh." with manual refresh. Individual sections may still render if partial data exists
- Error state — AI generation not complete: "This report's AI analysis is still being generated. Check back in a few minutes." with a spinner and estimated time remaining
- Disabled state: Previous week arrow is disabled/hidden when viewing week 1. Next week arrow is disabled/hidden when viewing a week beyond the user's current program week. The "Latest" button is disabled when already viewing the latest report
- Conditional visibility: The share button only appears when the report is fully generated and the user has share capabilities. The milestone alert only shows when the user is approaching a milestone. The "Next Week's Focus" section only shows if the report includes future-facing coaching

---

## Design System Notes

### Color Palette Usage Rules

- **Teal (`#00C4A7`)**: Reserved for score values only — the FORGE Optimisation Score, pillar scores, and score deltas. Never used for buttons, text, badges, or decorative elements. The one exception: the teal checkmark in the paywall feature list.
- **Ember (`#E8A400`)**: Reserved for CTAs, primary buttons, accents, and interactive elements. Never used for score displays. Used for the streak fire icon, XP badges, milestone indicators, and active states.
- **EmberDim (`rgba(232,164,0,0.12)`)**: Subtle ember background tint for selected states, highlighted cards, and accent areas.
- **Pillar Colors**: Each of the 9 pillars has its own distinct color. These are used for pillar badges, score bars, trend graphs, and pill labels. Never mix pillar colors — skin data always uses teal, style data always uses red, etc.
- **Surface Hierarchy**: `canvas` (`#0A0A0A`) → `surface` (`#141414`) → `raised` (`#1C1C1C`). Cards sit on `surface` backgrounds. Elevated/featured cards use `raised`. The main screen background is `canvas`.
- **Text Hierarchy**: `bone` (`#F5F5F5`) for primary text → `ash` (`#9CA3AF`) for secondary → `muted` (`#4B5563`) for tertiary.
- **Divider**: `rgba(255,255,255,0.08)` for card borders (0.5px). `border`: `rgba(255,255,255,0.12)` for input field borders.
- **Never mix**: Teal and ember should never appear in the same visual element. Ember is for CTAs, teal is for scores. They have distinct semantic purposes.

### Typography Rules

- **Primary font**: Inter for all body text, labels, headings, and UI elements. Imported from `@expo-google-fonts/inter`.
- **Display font**: SpaceGrotesk-Bold for the FORGE wordmark only. Used in splash, welcome header, paywall, and plan-reveal. Never used for body text or UI labels.
- **Size scale**: Only 6 sizes allowed — 64 (hero/displays only), 24 (titles), 17 (headings), 13 (body), 11 (captions), 9 (labels/eyebrows). No other font sizes.
- **Weight scale**: Only 2 weights allowed — 400 (regular) and 700 (bold). No 500, 600, or 800.
- **Letter spacing**: Hero scores use tight spacing (-2.2). Eyebrow labels use wide spacing (1.8). Body text uses normal spacing (0).
- **Line heights**: Hero (72), title (28), heading (24), body (20), caption (16), small (12).

### Flat Surfaces

- All cards use `Colors.surface` (`#141414`) background with `Colors.divider` (`rgba(255,255,255,0.08)`) borders at 0.5px.
- No box shadows, no `elevation` properties, no drop shadows on any element.
- Depth is created through: surface color contrast (canvas vs. surface vs. raised), border accents (ember/teal left borders on featured cards), animated mesh gradients (background only, on splash/score screens), SVG grain texture (subtle noise at 4.5% opacity).
- Never use: `shadowColor`, `shadowOffset`, `shadowOpacity`, `shadowRadius`, or `elevation` in React Native styles.

### Layout

- Horizontal screen padding: `Spacing.screen` = 24px on all screens.
- Vertical rhythm uses the spacing scale: `xs` (4), `sm` (8), `md` (12), `lg` (16), `xl` (20), `xxl` (24), `xxxl` (32).
- Card-to-card spacing: `Spacing.lg` (16px).
- Section-to-section spacing: `Spacing.xl` (20px) or `Spacing.xxl` (24px).
- Content within cards: `Spacing.md` (12px) or `Spacing.lg` (16px) padding.

### Buttons

- **PrimaryButton**: `Colors.ember` background, `Colors.bone` text (or dark text for contrast). Full-width with `Spacing.screen` margins. Height: 52px. Border radius: 12px. Text: body size (13px), weight 700. Disabled state: `Colors.muted` background, `Colors.ash` text.
- **SecondaryButton**: Transparent background, `Colors.border` outline (1px), `Colors.bone` text. Same dimensions as primary. Disabled: `Colors.muted` border, `Colors.muted` text.
- **Tertiary/Danger button**: `Colors.danger` background (10% opacity), `Colors.danger` text, `Colors.danger` border (1px). Used only for destructive actions (delete account).

### Cards

- **ForgeCard**: Base component wrapping content with `Colors.surface` background, `Colors.divider` border (0.5px), optional padding (`padding: Spacing.lg` by default, configurable via `padded` prop). Border radius: `Radius.lg` (8px) or `Radius.card` (12px). No shadows.
- **ForgeCard variants**: `accent` (ember left border, 3px), `featured` (raised background), `danger` (danger left border), `success` (success left border).

### Grain Overlay

- Used on: splash screen, welcome carousel, plan-loading, plan-reveal, and FORGE Score displays (progress tab hero).
- SVG noise pattern `GRAIN_SVG` rendered at 4.5% opacity as an overlay. Also configurable via `GrainLayers` for different intensities.
- Creates a subtle film-like texture that adds depth to flat dark surfaces without shadows.

### Mesh Gradient

- Animated mesh gradient backgrounds used on: splash screen, plan-loading, plan-reveal, estimated score, season complete.
- Composed of overlapping soft radial gradients in teal and ember tones at low opacity.
- Subtle animation (slow rotation/scaling, 8–12s cycle) to create a living, breathing backdrop.
- Purpose: provide depth and premium feel to key emotional moments in the user journey.
- Never overlaid on top of content — always behind (lowest z-index).

### Animation Principles

- **Entrance**: `cubic-bezier(0.16, 1, 0.3, 1)` (expo-out) for elements appearing on screen. Used for screen transitions, card reveals, and score count-ups.
- **State transitions**: `cubic-bezier(0.4, 0, 0.2, 1)` for interactive state changes (button presses, toggle switches).
- **Duration scale**: Fast (150ms) for micro-interactions, standard (250ms) for most transitions, slow (400ms) for reveals.
- **Spring configs**: Gentle (`damping: 20, stiffness: 100`) for bounces, snappy (`damping: 15, stiffness: 200`) for button presses, bouncy (`damping: 10, stiffness: 150`) for celebrations.
- **Score count-up**: Animated number counter, 1.5s duration, ease-out. Starts from 0, counts to the target value.

### Code Implementation Reference

All design tokens are defined in `src/constants/design.ts` and imported as:
```typescript
import { Colors, Typography, Spacing, Radius, Animation, Easing, GRAIN_SVG, GrainLayers, SpringConfig } from "@/constants/design"
```

No hardcoded color, spacing, font size, or radius values are permitted anywhere in the codebase. Always reference the token constants.
