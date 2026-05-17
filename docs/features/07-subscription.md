# Feature: Subscription & Paywall

> Monetize the app through a single $11/mo Basic tier via RevenueCat. Handle purchase, restore, expiry, and server-side validation.

Feature: Subscription & Paywall. Actor: Guest → User. Phase: MVP.
Implementation: `app/(auth)/paywall.tsx`, `src/lib/revenuecat.ts`, `src/hooks/useSubscription.ts`, `supabase/functions/revenuecat-webhook/index.ts`
Purpose: Monetize the app through a single $11/mo Basic tier via RevenueCat. Handle purchase, restore, expiry, and server-side validation.

---

## 1.1 Paywall Screen

The paywall screen (`app/(auth)/paywall.tsx`) appears after the user confirms their generated plan on the plan-reveal screen. It is the final onboarding gate before the user enters the main app. The screen reads the cached plan and quiz answers to personalise the value proposition — surfacing the user's top concerns, estimated time commitment, and key outcomes. A MeshGradient background provides visual distinction from the rest of the onboarding flow. The screen captures a `PAYWALL_VIEWED` analytics event on mount. At the bottom, a gold EmberButton triggers the $11/mo purchase; a secondary Restore Purchases button sits below. The screen handles three error states: purchase failure (inline error message with retry), restore failure (inline message), and already-subscribed (auto-redirect to app). The user cannot navigate back — the paywall is a one-way gate.

- Screen captures `PAYWALL_VIEWED` PostHog event on mount
- Personalised messaging derived from cached quiz answers (concerns, time budget) and plan cache
- 5 static outcome bullet points displayed: "Track 9 measurable appearance areas", "See progress via photo check-in every 3 days", "AI coaching reports every Sunday", "Daily tasks calibrated to your goals", "Score updates with every check-in"
- Gold EmberButton triggers `purchase()` from `useSubscription` hook
- Secondary "Restore Purchases" text button triggers `restore()` from `useSubscription` hook
- Already-subscribed users auto-redirect to `/(app)/(tabs)` (detected via `useSubscription().data.isActive`)
- Purchase-in-progress shows ActivityIndicator on the button
- Inline error state for purchase/restore failures, rendered near the button
- Cannot navigate back — the screen is intentionally a dead-end until purchase/restore succeeds

---

## 1.2 Purchase Flow

The purchase flow is orchestrated by `src/lib/revenuecat.ts` — a thin wrapper around the RevenueCat SDK (`react-native-purchases`). The entry point is `purchaseBasic()`, called by the `useSubscription` hook. The function fetches the current offering, finds the `basic_monthly` package within it, and calls `Purchases.purchasePackage()`. On success, it reads the `basic` entitlement from the customer info, checks for an active entitlement, extracts the expiration date, and syncs the subscription status to the `users` table (`subscription_tier = "premium"`, `subscription_provider = "revenuecat"`, `subscription_expires_at`). The `useSubscription` hook wraps this with loading states (`isPurchasing`), error handling with user-readable messages, and local state updates so the UI reactively shows the new active subscription. On successful purchase, the paywall screen schedules all push notifications via `useNotifications().setupNotifications(user)` and navigates to `/(app)/(tabs)`. A `SUBSCRIPTION_STARTED` PostHog event is captured.

- `purchaseBasic()` fetches offerings via `Purchases.getOfferings()`, locates `basic_monthly` package
- Calls `Purchases.purchasePackage(packageToPurchase)` to present the native iOS/Android paywall
- On success, reads `customerInfo.entitlements.active["basic"]` to verify
- Syncs to `users` table: `subscription_tier = "premium"`, `subscription_provider = "revenuecat"`, `subscription_expires_at = <date>`
- Returns `{ active: boolean; expiresAt?: string }` to caller
- `useSubscription` hook tracks `isPurchasing` boolean during the flow
- Error messages are user-friendly: "No offering available. Please try again later.", "Purchase failed"
- Post-purchase, paywall screen calls `setupNotifications(user)` then `router.replace("/(app)/(tabs)")`
- PostHog `SUBSCRIPTION_STARTED` event fired on successful purchase

---

## 1.3 Restore Flow

The restore flow allows returning users on a new device to recover their existing subscription without paying again. `restorePurchases()` calls `Purchases.restorePurchases()`, checks for the active `basic` entitlement in the returned customer info, syncs the status to the `users` table if active, and returns the active status and expiration date. The `useSubscription` hook wraps this with `isRestoring` loading state and error handling. The paywall screen's "Restore Purchases" button triggers this flow. If the restore finds an active entitlement, the user is auto-redirected to the app. If it finds no active entitlement, an inline message informs the user (they remain on the paywall screen to purchase).

- `restorePurchases()` calls `Purchases.restorePurchases()` (no user login required — RevenueCat identifies by device)
- Checks `customerInfo.entitlements.active["basic"]` for active subscription
- Syncs to `users` table on success (same sync as purchase flow)
- Returns `{ active: boolean; expiresAt?: string }`
- `useSubscription` hook tracks `isRestoring` boolean
- On active restore: auto-redirect to `/(app)/(tabs)`
- On inactive restore: inline message "No active subscription found. Purchase below to continue."
- Error handling: "Could not restore purchases." displayed near the restore button

---

## 1.4 RevenueCat Webhook

The `supabase/functions/revenuecat-webhook/index.ts` edge function receives server-side events from RevenueCat to keep the `users` table in sync even when the client isn't active. It validates the incoming request with a `REVENUECAT_WEBHOOK_SECRET` environment variable (checked as `Authorization: Bearer <secret>` against the env var). It only processes five event types: `INITIAL_PURCHASE`, `RENEWAL`, `CANCELLATION`, `EXPIRATION`, `NON_RENEWING_PURCHASE`. On non-terminal events (INITIAL_PURCHASE, RENEWAL, NON_RENEWING_PURCHASE), it sets `subscription_tier = "premium"`. On terminal events (CANCELLATION, EXPIRATION), it sets `subscription_tier = "none"` and nullifies `subscription_expires_at`. The webhook operates as `service_role` via the Supabase client, bypassing RLS. Unknown or unhandled events are logged and return `200 { received: true }` without a DB update — the webhook is non-disruptive for future event types. OPTIONS preflight requests are handled for CORS.

- Validates incoming request with `Authorization: Bearer <REVENUECAT_WEBHOOK_SECRET>` header
- CORS headers on all responses (`Access-Control-Allow-Origin: *`)
- Handles 5 event types: `INITIAL_PURCHASE`, `RENEWAL`, `NON_RENEWING_PURCHASE` → tier = "premium"; `CANCELLATION`, `EXPIRATION` → tier = "none"
- Uses `service_role` key via `SUPABASE_SERVICE_ROLE_KEY` env var, bypassing RLS
- Unrecognised events logged and return `200 { received: true }` (non-disruptive for future types)
- Missing `app_user_id` returns 400
- DB update failure returns 500 with error message
- OPTIONS preflight returns 200 for CORS
- `subscription_provider` always set to `"revenuecat"`
- Logs each processed event with user ID, event type, and resulting tier

---

## 1.5 Dev Bypass Mode

During local development and testing (where RevenueCat requires an EAS dev build), the `isDevBypass()` function in `src/lib/revenuecat.ts` detects dev mode and short-circuits all SDK calls. The check is `typeof __DEV__ !== "undefined" && __DEV__ && process.env.EXPO_PUBLIC_APP_ENV !== "production"`. When active, `configure()` skips SDK initialisation, `purchaseBasic()` returns `{ active: true }` immediately, `restorePurchases()` returns `{ active: true }` immediately, and `getCustomerInfo()` returns `{ active: true }` immediately. All bypass paths log a `[RevenueCat] DEV BYPASS` console message. This allows the full onboarding flow to be tested in Expo Go without RevenueCat SDK dependencies.

- `isDevBypass()` returns true when `__DEV__` is true and `EXPO_PUBLIC_APP_ENV !== "production"`
- `configure()`: skips `Purchases.logIn()` (SDK not initialised in Expo Go)
- `purchaseBasic()`: returns `{ active: true }` immediately — simulates successful purchase
- `restorePurchases()`: returns `{ active: true }` immediately — simulates active subscription found
- `getCustomerInfo()`: returns `{ active: true }` immediately — simulates active subscription
- All bypass paths log `[RevenueCat] DEV BYPASS` with context
- This bypass is transparent to the `useSubscription` hook — it receives the same return shape

---

## 1.6 Subscription Status Sync

The `useSubscription` hook (`src/hooks/useSubscription.ts`) maintains a dual-source subscription status check: it queries both the local `users` table and the RevenueCat SDK, and considers the subscription active if either source reports active. On mount and whenever the user object changes, `fetchSubscriptionStatus()` runs both checks in parallel. The DB check reads `subscription_tier` and `subscription_expires_at` from the `users` table; if the tier is not "premium" or "basic", or the expiration is in the past, the DB side reports inactive. The SDK check calls `getCustomerInfo()`; if it fails, the hook warns and falls back to DB-only. The combined result: `isActive = dbActive || sdkActive`, with the expiry date favouring the SDK value. The hook exposes `refetch()` for callers to force a re-check (e.g., after the webhook updates the DB). On sign-out, the subscription state resets to inactive via the `useUserStore` reset flow.

- `fetchSubscriptionStatus()` runs on mount and when `user` changes
- DB check: reads `users.subscription_tier` and `users.subscription_expires_at`, marks active only if tier is "premium" or "basic" and not expired
- SDK check: calls `getCustomerInfo()` from RevenueCat wrapper; on failure, falls back to DB-only with `console.warn`
- Combined result: `isActive = dbActive || sdkActive`, `expiresAt = sdkExpiresAt ?? dbExpiresAt`
- `tier` is always `"basic"` when active, `"none"` when inactive (no tier gating, single Basic plan)
- `refetch()` exposed for callers to force status refresh
- `loading` true during initial fetch, false after both sources resolve
- `error` populated with user-readable message on fetch failure
- Returns `SubscriptionData` with `isActive`, `expiresAt`, `tier`
