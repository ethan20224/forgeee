# Flow: Onboarding

> Complete onboarding journey: splash → welcome → quiz → signup → plan-loading → plan-reveal → paywall → app.

Flow: Onboarding. Actor: Guest. Trigger: App first launch (no session). End state: User at main app tabs, subscribed, notifications configured.

---

## Happy Path

```
1. App launch (no session)
   └─> Splash screen (FORGE wordmark, animated progress bar)
       └─> Welcome slides (3 swipable slides)
           ├─ Slide 1: "Your appearance, measured." — brand intro
           ├─ Slide 2: "90 days. 9 pillars. One score." — program overview
           └─ Slide 3: "Science-backed. AI-powered. Human-led." — value proposition
               └─> Quiz screen (7 questions, step-by-step)
                   1. "What's your main goal?" (multi-select: skin, grooming, hair, style, posture)
                   2. "How would you rate your current routine?" (1–5 scale)
                   3. "How much time can you commit daily?" (5min / 15min / 30min / 60min)
                   4. "What's your face shape?" (visual selector: oval, round, square, heart, diamond, triangle, oblong)
                   5. "What's your biggest frustration with your current appearance routine?" (free text)
                   6. "How did you hear about FORGE?" (social media, friend referral, search, other)
                   7. "What's your age range?" (18–24, 25–34, 35–44, 45+)
                   └─> Estimated score reveal (FORGE Score animation rising to estimated value, pillar breakdown)
                       └─> Signup screen (name, email, password)
                           ├─ Validation: name 1–100 chars, valid email, password ≥8 chars
                           ├─ On submit: creates Supabase Auth user + inserts users row (onboarded=false) + progress row (all scores=50)
                           └─> Plan loading screen (rotating coaching messages + progress spinner)
                               ├─ Codex AI generates 90-day plan from quiz answers + Master Task Library
                               ├─ Plan saved to database (transactional: plan row + 90 days of tasks + task_library_selections)
                               └─> Plan reveal screen
                                   ├─ Displays: focus areas, expected improvements, AI compliment
                                   ├─ User reviews plan → taps "Begin Transformation"
                                   ├─ Sets onboarded=true on users table
                                   ├─ Captures SUBSCRIPTION_STARTED event
                                   └─> Paywall screen
                                       ├─ Personalised messaging from quiz + plan cache
                                       ├─ User taps "Subscribe $11/mo" → RevenueCat purchase flow
                                       ├─ Purchase succeeds → schedule push notifications → navigate to /(app)/(tabs)
                                       └─ End state: User on home tab, subscribed, notifications configured
```

---

## Alternate Paths

### Returning User Logs In
```
App opens → session exists (Supabase auth) → query users table → user.onboarded?
├─ YES → navigate to /(app)/(tabs) directly
└─ NO → check plan_start_date?
    ├─ YES → plan exists, user needs to complete paywall → navigate to paywall
    └─ NO → plan not yet created → navigate to welcome (restart onboarding)
```

### Quiz Draft Resume
```
User closes app mid-quiz → quiz answers saved to AsyncStorage as draft
App reopens → welcome screen detects AsyncStorage quiz draft
├─ Prompt: "You have a saved quiz. Continue where you left off?"
│   ├─ Yes → jump to first unanswered quiz question
│   └─ No → discard draft, start fresh quiz
```

### Paywall Dismissed
```
User reaches paywall → taps back/close (if available) → stays on paywall
No back-navigation from paywall in the auth flow stack
If modal dismiss attempted → paywall remains, no app access
User must purchase or restore to proceed
```

### Baseline Photo Mid-Onboarding (Edge Case Recovery)
```
Scenario: User's onboarding was interrupted after plan-reveal but before paywall completion
User somehow reaches (auth)/baseline-photo.tsx (edge case route)
├─ If onboarded=false AND plan exists → route to paywall (bypass baseline photo — deferred to day 3)
├─ If onboarded=true → route to /(app)/(tabs) (normal app entry)
└─ If no session → route to welcome
The (auth)/baseline-photo.tsx route exists only for edge case recovery; normal flow defers baseline to day 3 in-app
```

---

## Error States

| Error | Detection | User Experience |
|-------|-----------|-----------------|
| **Network failure during plan generation** | `planGenerator.ts` fetch timeout or network error | Loading screen shows "Connection lost. Retrying..." with auto-retry countdown (3 attempts, 5s apart). On final failure: "Could not generate your plan. Please check your connection and try again." with "Retry" button. |
| **Claude API error** | `callClaude()` returns error or invalid JSON | Loading screen shows "Our AI is taking longer than expected..." (first 20s). On failure: "Plan generation hit a snag. This is on our side — please try again." with "Retry" button. Logs error to `claude_api_calls` audit table. |
| **RevenueCat unavailable** | `purchaseBasic()` throws, `getOfferings()` returns null | Paywall shows "Payment service temporarily unavailable. Please try again in a moment." with "Retry" button. Restore button still available. |
| **DB save failure** | `savePlanToDatabase()` transaction fails | Plan reveal screen shows "Could not save your plan. Your quiz answers are safe." with "Retry Save" button. Quiz answers and plan cache preserved in memory. Plan is NOT marked as saved — user can retry. |
| **Ghost user (auth but no profile)** | `getCurrentUser()` returns null despite valid session | Sign-in flow detects missing profile row → upserts recovery row with `onboarded=false` → resumes onboarding at welcome screen. User sees signup screen pre-filled with email, prompted to complete onboarding. |

### General Error Handling Rules
- Every async operation has a try/catch with user-visible error message
- Error messages are actionable: tell the user what happened AND what to do
- Retry buttons always present on error screens
- No silent failures — all errors are logged AND surfaced to user
- Network errors auto-retry up to 3 times before showing user-facing error
