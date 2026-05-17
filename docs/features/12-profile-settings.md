# Feature: Profile & Settings

> User can view their profile, manage account settings, sign out, or delete their account with full data cleanup.

Feature: Profile & Settings. Actor: User (Member). Phase: MVP.
Implementation: `app/(app)/(tabs)/profile.tsx`, `src/hooks/useAccount.ts`, `src/lib/auth.ts`
Purpose: User can view their profile, manage account settings, sign out, or delete their account with full data cleanup.

---

## 1.1 Profile Display (Name, Email, Subscription Status)

The profile screen (`app/(app)/(tabs)/profile.tsx`) displays the user's name, email, subscription tier and status, season and program day, and referral code. It reads from `useUserStore` for the user profile and `useSubscription` for subscription status. The subscription section shows: (a) the plan name ("Basic"), (b) the status ("Active" or "Inactive"), (c) the renewal/expiry date if available, and (d) a "Manage Subscription" link if on iOS. The profile screen handles loading state (skeleton placeholders while user data hydrates) and error state (retry button if the user fetch fails). The user's referral code is displayed with a copy-to-clipboard action. The screen also shows the app version from `expo-constants`.

- Displays: name, email, season number, program day, referral code (with copy button)
- Subscription section: tier ("Basic"), status ("Active"/"Inactive"), renewal/expiry date
- Subscription data from `useSubscription` hook (dual-source: DB + RevenueCat SDK)
- "Manage Subscription" link for iOS users (opens system settings)
- Loading state: skeleton placeholders while stores hydrate
- Error state: inline error message with retry button
- App version displayed from `expo-constants`

---

## 1.2 Account Deletion (Cascading Delete Across All Tables)

Account deletion is a destructive, irreversible operation that removes all user data across every database table. The `deleteAccount(userId)` function in `src/lib/auth.ts` first verifies the caller's session matches the `userId` being deleted (prevents unauthorised deletion via arbitrary ID passing). It then deletes rows from 12 tables in dependency-safe order: `pending_notifications`, `season_events`, `challenge_progress`, `achievements`, `cycles`, `daily_tasks`, `weekly_reports`, `micro_sprints`, `quiz_answers`, `plans`, `progress`, `users`. Each table deletion is independent — if one fails, the function logs a warning and continues to the next table (best-effort cleanup). After DB cleanup, the function signs the user out of Supabase Auth locally. The auth user record in Supabase Auth is not deleted client-side (requires service role key) — it can be cleaned up via an Edge Function or admin dashboard. After deletion, the user is redirected to the welcome screen.

- Session verification: `session.user.id === userId` before any deletion — prevents cross-account deletion
- 12 tables deleted in order: `pending_notifications`, `season_events`, `challenge_progress`, `achievements`, `cycles`, `daily_tasks`, `weekly_reports`, `micro_sprints`, `quiz_answers`, `plans`, `progress`, `users`
- Each table deletion uses `supabase.from(table).delete().eq("user_id", userId)`
- Best-effort cleanup: if one table delete fails, the function warns and continues
- Supabase Auth user record not deleted client-side (requires service role) — cleaned up server-side
- Signs out locally via `supabase.auth.signOut()` after data deletion
- Returns `{ error: string | null }` — user-redirectable error if deletion fails

---

## 1.3 Sign Out (Store Reset, Cache Clear, Notification Cancel, Analytics Reset)

Sign out performs a comprehensive cleanup of all local state. The `signOut()` function in `src/lib/auth.ts` executes in order:

1. **Cancel notifications**: `cancelAll()` removes all scheduled push notifications.
2. **End Live Activity**: `endStreakActivity()` dismisses the Streak Live Activity if active.
3. **Reset stores**: `useUserStore.reset()`, `useProgressStore.reset()`, `useProgramStore.reset()` clear all Zustand state.
4. **Clear caches**: `clearCachedPlan()` and `clearCachedBaselineAnalysis()` wipe in-memory plan/analysis data.
5. **Sign out auth**: `supabase.auth.signOut()` clears the Supabase session and SecureStore tokens.
6. **Reset analytics**: PostHog `reset()` is called to clear the distinct ID (called in the sign-out UI handler, not in `auth.ts`).

The `useAccount` hook wraps this with `isSigningOut` loading state and user-readable error messages. The sign-out button on the profile screen shows a confirmation dialog before proceeding.

- `cancelAll()` → `endStreakActivity()` → store resets → cache clears → `supabase.auth.signOut()`
- Three Zustand stores reset: `useUserStore`, `useProgressStore`, `useProgramStore`
- Two in-memory caches cleared: `clearCachedPlan()`, `clearCachedBaselineAnalysis()`
- PostHog `reset()` called in the sign-out handler (not in `auth.ts`)
- `useAccount` hook provides `signOut()` with `isSigningOut` loading state
- Confirmation dialog before executing sign-out on profile screen
- Error handling: "Failed to sign out" message with retry option

---

## 1.4 Settings (Timezone, App Version)

The profile/settings screen surfaces read-only information about the user's account environment. The timezone displayed is the value captured at signup and stored in `users.timezone` (not the device's current timezone — this is historical, not dynamic). The app version is read from `expo-constants`'s `expoConfig.version` at build time. The settings section also includes a link to the FORGE privacy policy and terms of service.

- Timezone: read from `users.timezone` (captured at signup) — displayed as read-only
- App version: from `expo-constants`'s `expoConfig.version` — displayed as read-only
- Privacy policy link: opens external URL in device browser
- Terms of service link: opens external URL in device browser
- No editable settings at MVP — all fields are read-only informational
