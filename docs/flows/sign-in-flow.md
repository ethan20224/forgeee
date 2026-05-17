# Flow: Sign In

> Returning user sign-in, auth state recovery, and routing based on onboarding state.

Flow: Sign In. Actor: Returning User. Trigger: User opens app with expired/valid session. End state: User at correct screen based on onboarding state.

---

## Happy Path

```
1. App opens (cold start or background → foreground)
   └─> Root layout (_layout.tsx) mounts
       └─> Auth state check
           ├─ supabase.auth.onAuthStateChange listener registered
           └─> supabase.auth.getSession() called (storage-based recovery)
               └─> Session found?
                   ├─ YES: Session exists
                   │   └─> Query users table: SELECT * FROM users WHERE id = session.user.id
                   │       └─> User row found?
                   │           ├─ YES: User profile exists
                   │           │   └─> Check user.onboarded
                   │           │       ├─ YES: Onboarding complete
                   │           │       │   └─> Navigate to /(app)/(tabs) — main app
                   │           │       │       ├─ Set user in useUserStore
                   │           │       │       ├─ Hydrate progress (useProgress)
                   │           │       │       ├─ Hydrate program (useProgramStore)
                   │           │       │       ├─ Check program day advancement
                   │           │       │       ├─ Refresh subscription status (useSubscription)
                   │           │       │       └─ End state: User on home tab
                   │           │       └─ NO: Onboarding incomplete
                   │           │           └─> Check plan_start_date?
                   │           │               ├─ YES: Plan exists → navigate to paywall
                   │           │               │   └─ User must complete subscription to enter app
                   │           │               └─ NO: No plan → navigate to welcome screen
                   │           │                   └─ Resume onboarding from start (or quiz draft)
                   │           └─ NO: Ghost user (auth exists, no profile row)
                   │               └─> Upsert recovery profile row
                   │                   ├─ Insert users row with onboarded=false
                   │                   ├─ Insert progress row with default scores (all 50)
                   │                   └─ Navigate to welcome screen (start onboarding)
                   └─ NO: No session
                       └─> Navigate to welcome screen (guest onboarding)
```

---

## Alternate Paths

### Expired Session
```
App opens → onAuthStateChange fires with event: SIGNED_OUT or TOKEN_REFRESH_FAILED
├─ Listener detects session change
├─ Clears Zustand stores (useUserStore, useProgressStore, useProgramStore)
├─ Clears caches (planCache, baselineAnalysis)
├─ Redirects to welcome screen (auth group)
└─ User sees login option: "Already have an account? Sign in."
```

### Session Recovery Fallback
```
getSession() returned null but SecureStore may have stale token
├─ Attempt signInWithPassword with stored credentials? NO — credentials not stored
├─ Instead: show welcome screen with "Sign In" button prominent
├─ User manually enters email/password → signIn() called
│   ├─ Validates credentials with Supabase Auth
│   ├─ Fetches user profile row
│   └─ Routes based on onboarded flag (same logic as happy path)
└─ Welcome screen shows clear "Returning user? Sign in" link at bottom
```

### Ghost User Recovery
```
Auth session valid, but users table has no row for this auth.uid()
├─ Detection: SELECT * FROM users WHERE id = auth.uid() returns empty
├─ Recovery: upsert profile row
│   ├─ INSERT INTO users (id, email, name) with onboarded=false
│   │   └─ Uses auth.user.email and auth.user.user_metadata.name if available
│   ├─ INSERT INTO progress (user_id, all_scores=50) — best-effort, non-blocking
│   └─ Returns repaired user row
├─ Routes to welcome screen (onboarded=false, no plan_start_date)
└─ Ghost user cause: previous signup partially failed (auth created, profile didn't)
```

### Post-Signout Return
```
User signed out manually → app shows welcome screen
├─ All stores reset, caches cleared, notifications cancelled
├─ User can tap "Sign In" → signIn screen with email/password fields
├─ On successful sign-in → same routing logic as happy path
└─ Previous data recovered from Supabase (nothing lost — all server-side)
```

---

## Error States

| Error | Detection | User Experience |
|-------|-----------|-----------------|
| **DB fetch timeout (retry once)** | `getCurrentUser()` fetch exceeds 5s or Supabase returns timeout | First attempt: waits 1 second, retries once. On second failure: "Could not load your account. Please check your connection." with "Try Again" button. User stays on loading/splash screen. After 3 manual retries: "Still having trouble? Contact support." |
| **Supabase Auth server down** | `getSession()` or `signIn()` returns network error or 503 | Welcome screen shows error banner: "We're having trouble connecting. Please try again shortly." Auto-retry countdown: 10s intervals, up to 6 attempts. On persistent failure: "FORGE is temporarily unavailable. We're working on it." |
| **Ghost user profile upsert fails** | Supabase upsert returns error (e.g., RLS not yet applied, schema mismatch) | Show error screen: "Account recovery failed. Please sign up again." with "Start Over" button that clears session and navigates to signup flow. The partial auth user is orphaned but harmless — next signup with same email will link to it. |
| **Session exists but user.onboarded is NULL** | `onboarded` column is NULL (not false) — corrupted/missing value | Treat as onboarded=false for safety. Navigate to welcome screen. The `onboarded` column has a NOT NULL DEFAULT false constraint — NULL indicates a migration issue. Log warning to console for debugging. |
