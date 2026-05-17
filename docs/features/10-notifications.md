# Feature: Push Notifications

> Schedule guilt-free, factual push notifications that remind users of cycle check-ins and weekly reports without using manipulative language.

Feature: Push Notifications. Actor: System → User. Phase: MVP.
Implementation: `src/services/notifications/notificationService.ts`, `src/hooks/useNotifications.ts`
Purpose: Schedule guilt-free, factual push notifications that remind users of cycle check-ins and weekly reports without using manipulative language.

---

## 1.1 Permission Request (Post-Paywall)

Notification permissions are requested after a successful RevenueCat purchase — never before. The `requestPermissions()` function in `notificationService.ts` uses `expo-notifications` to first check existing permission status, and only prompts the system dialog if permissions aren't already granted. The function returns a boolean indicating whether permissions were granted. On iOS, this triggers the native system permission dialog ("FORGE would like to send you notifications"). If the user denies, notification scheduling is silently skipped — the app remains fully functional without notifications. The permission request is called from the paywall screen's post-purchase flow via `useNotifications().setupNotifications(user)`.

- `requestPermissions()` checks existing status via `getPermissionsAsync()`, only prompts if not already granted
- Calls `requestPermissionsAsync()` only when needed — respects prior user choice
- Returns `boolean`: true if granted, false if denied or errored
- Called post-paywall (after `purchaseBasic()` succeeds) — not during onboarding intro
- Denial is non-blocking: app functions fully without notifications
- `useNotifications` hook wraps this with error-tolerant callbacks (failures are `console.warn`, not thrown)

---

## 1.2 Cycle Prompts (Every 3 Days, 10am)

Cycle check-in reminders are scheduled for every 3 days at 10:00 AM local time. The `scheduleCyclePrompt()` function calculates cycle dates based on the user's `plan_start_date`. If no start date is available (edge case: plan not yet finalised), it schedules a single one-off notification for the next 10:00 AM. With a start date, it schedules the next 4 cycles (12 days ahead) — each notification is a non-repeating `DATE` trigger at 10:00 AM on the target cycle day. Past dates are skipped. The notification content is factual: title "Cycle photo today.", body "Same angle, same lighting." No urgency, no FOMO language. The notification carries `data: { type: "cycle-prompt", userId, cycleDay }` for deep-linking to the cycle check-in screen.

- Cycle interval: every 3 days (constant `CYCLE_INTERVAL_DAYS = 3`)
- Scheduled 12 days ahead (`SCHEDULE_AHEAD_DAYS = 12`, ~4 cycles)
- Trigger: `DATE` type at 10:00 AM local time on target cycle day, non-repeating
- Falls back to single one-off at next 10am if `plan_start_date` is null
- Content: title "Cycle photo today.", body "Same angle, same lighting."
- Notification data: `{ type: "cycle-prompt", userId, cycleDay }` for deep-linking
- Past dates automatically skipped during schedule loop
- Logs count of scheduled prompts per user

---

## 1.3 Weekly Report Notification (Sun 9am, Repeating)

A weekly notification reminds users that their coaching report is ready. The `scheduleWeeklyReport()` function schedules a single repeating `CALENDAR` trigger for every Sunday at 9:00 AM. The trigger uses `weekday: 1` (Monday = 2 in expo-notifications, Sunday = 1), hour 9, minute 0. The notification is set to repeat indefinitely — it fires every Sunday at 9am until cancelled. Content is minimal: title "Weekly report ready." with an empty body. The notification data carries `{ type: "weekly-report", userId }` for deep-linking to the report viewer.

- Single repeating notification via `CALENDAR` trigger
- Schedule: Sunday (weekday 1) at 9:00 AM, repeats indefinitely
- Content: title "Weekly report ready.", body ""
- Notification data: `{ type: "weekly-report", userId }` for deep-linking
- One notification per user — no per-week scheduling (repeating single trigger)
- Sound and badge enabled

---

## 1.4 Day-1 Push

A single one-off notification fires at 7:00 AM on the user's first program day. The `scheduleDay1Push()` function schedules a `CALENDAR` trigger at hour 7, minute 0 with `repeats: false`. The notification is scheduled immediately when the user completes paywall → notification setup, so it fires on whatever day the user signed up (the next 7:00 AM if the current time is past 7am). Content: title "Welcome to Day 1", body "Your transformation starts now".

- One-off `CALENDAR` trigger at 7:00 AM, non-repeating
- Scheduled during post-paywall notification setup alongside cycle and weekly triggers
- Content: title "Welcome to Day 1", body "Your transformation starts now"
- Notification data: `{ type: "day-1-push", userId }`

---

## 1.5 Guilt-Free Language Policy

All notification text follows a strict guilt-free policy: no urgency, no FOMO, no shaming, no "we miss you", no "your streak is at risk", no "don't lose progress". Instead, notifications use factual, flat language. The cycle prompt says "Cycle photo today. Same angle, same lighting." — an instruction, not a plea. The weekly report says "Weekly report ready." — a notification, not a reward to chase. The day-1 push says "Your transformation starts now" — declarative and affirming. The streak-risk notification (formerly scheduled at 9pm) has been entirely removed from the codebase. The `scheduleAll()` function in `notificationService.ts` calls exactly three schedulers: cycle, weekly, and day-1. No "at risk", no "come back", no "keep going" — anywhere in the notification system.

- No guilt language: no "we miss you", "streak at risk", "don't lose progress", "come back", "keep going"
- Cycle prompt: "Cycle photo today. Same angle, same lighting." — instructive, factual
- Weekly report: "Weekly report ready." — minimal, informative
- Day-1 push: "Welcome to Day 1. Your transformation starts now." — declarative, peaceful
- Streak-risk notification permanently removed (previously at 9pm) — no replacement
- `scheduleAll()` calls exactly 3 schedulers: `scheduleCyclePrompt`, `scheduleWeeklyReport`, `scheduleDay1Push`
- Policy documented in notification service file comment: "No 'at risk', 'miss you', 'come back', 'keep going' language anywhere."

---

## 1.6 Notification Cancellation (on Sign Out)

When a user signs out, all scheduled notifications must be cancelled to prevent the next user on the device from receiving the previous user's reminders. The `signOut()` function in `src/lib/auth.ts` calls `cancelAll()` from `notificationService.ts` before clearing session state. `cancelAll()` calls `Notifications.cancelAllScheduledNotificationsAsync()` from `expo-notifications`, which removes every scheduled notification regardless of type. This is called before `useUserStore.reset()`, `useProgressStore.reset()`, and `useProgramStore.reset()` to ensure no stale notification data remains.

- `cancelAll()` called as first step in `signOut()` (before store resets)
- Uses `Notifications.cancelAllScheduledNotificationsAsync()` — removes all scheduled notifications
- Also cancels the Live Activity via `endStreakActivity()` call in signOut
- Errors during cancellation are caught and logged — sign-out proceeds regardless
- On sign-out, notification permissions are not revoked (system-level) — they persist for next login

---

## 1.7 Timezone-Based Scheduling

All notifications are scheduled relative to the user's local timezone. The user's timezone is captured at signup via `getDeviceTimezone()` (`Intl.DateTimeFormat().resolvedOptions().timeZone`) and stored in `users.timezone`. The cycle prompt scheduling uses this timezone to calculate local-time trigger dates: the `plan_start_date` is parsed as a local date, and cycle dates are computed by adding days to that date. The weekly report uses `CALENDAR` triggers which fire at the specified hour in the device's current timezone. The `getDeviceTimezone()` function falls back to `"UTC"` if the runtime cannot determine the timezone (e.g., web platform limitations).

- Timezone captured at signup via `Intl.DateTimeFormat().resolvedOptions().timeZone`
- Stored in `users.timezone` column
- Fallback to `"UTC"` if runtime detection fails
- Cycle prompt scheduling uses stored timezone + plan_start_date for local-time date calculation
- Weekly report and day-1 push use `CALENDAR` triggers (device-local time)
- Timezone changes (e.g., travel): notifications refire at the device's current timezone — no re-scheduling needed for CALENDAR triggers; cycle DATE triggers are pre-calculated and won't adjust mid-flight
