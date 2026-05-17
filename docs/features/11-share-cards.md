# Feature: Share Cards

> Users can generate and share visual cards showing their FORGE Score, pillar breakdown, and progress for social media sharing.

Feature: Share Cards. Actor: User (Member). Phase: MVP.
Implementation: `app/(app)/share-card.tsx`, `src/services/share/shareService.ts`, `src/hooks/useShareCard.ts`, `src/components/ui/ShareScoreCard.tsx`, `src/components/ui/ChallengeShareCard.tsx`
Purpose: Users can generate and share visual cards showing their FORGE Score, pillar breakdown, and progress for social media sharing.

---

## 1.1 Score Share Card

The score share card (`ShareScoreCard` component) renders the user's FORGE Optimisation Score, top pillar, weakest pillar, streak count, XP level, and a referral call-to-action onto a styled card. The card uses a dark surface (`Colors.surface = #141414`) with the FORGE wordmark, the large hero-scored optimisation score (64px, weight 700), and a compact pillar breakdown. The card is designed at a 9:16 portrait aspect ratio (720x1280 for standard share, 1080x1920 for high-res). The `generateShareCard()` function in `shareService.ts` captures the card view via `react-native-view-shot`'s `captureRef()`, outputting a PNG temp file. The card includes: (a) FORGE wordmark top, (b) season and day counter, (c) optimisation score as large number with "+X" delta, (d) streak count and XP level badges, (e) "top pillar" and "weakest pillar" with scores, (f) referral code at bottom as `forge.app/r/{code}`.

- `ShareScoreCard` component renders the card layout using standard design tokens
- Rendered at 720x1280 (standard) or 1080x1920 (high-res) via `react-native-view-shot`
- `captureRef()` captures the rendered view as PNG temp file
- Card elements: wordmark, season/day, optimisation score (hero size), delta, streak, XP level, pillar breakdown, referral code
- Dark surface background (`#141414`), teal for scores, gold for referral CTA
- Inter font, flat dark surfaces, no shadows — consistent with FORGE design language

---

## 1.2 Challenge Share Card

The challenge share card (`ChallengeShareCard` component) renders a card celebrating a completed challenge or streak milestone. It displays the challenge name, an icon representation, the user's progress (e.g., "7/7 days"), and a referral invitation. The `shareChallenge()` function in `shareService.ts` generates a text-based share message that includes the challenge name, progress fraction, a competitive nudge ("think you can beat my streak?"), and the referral link. The text-based sharing uses React Native's `Share.share()` API for platforms where image sharing isn't available or preferred. The `shareStreakMilestone()` function similarly formats a streak milestone for text sharing. Both functions check `isAvailableAsync()` before calling `Share.share()` to avoid crashes on platforms without sharing support.

- `ChallengeShareCard` component: challenge name, icon, progress fraction, referral code
- `shareChallenge()`: text-based share via `Share.share()` — includes challenge name, progress, and referral link
- `shareStreakMilestone()`: text-based share for streak milestones — includes streak days and referral link
- Both functions check `isAvailableAsync()` before calling `Share.share()`
- Error handling: "Sharing is not available on this device." if platform lacks sharing
- Referral code embedded as `forge.app/r/{referralCode}` in all share messages

---

## 1.3 Card Rendering (react-native-view-shot)

Card generation uses `react-native-view-shot` to capture the rendered React Native view as a PNG image. The `generateShareCard()` function takes a React ref to the card view and a user ID. It calls `captureRef(ref, { format: "png", quality: 1, result: "tmpfile", height: 1280, width: 720 })` to produce a temporary PNG file at the standard share resolution. The `generateHighResShareCard()` variant outputs at 1920x1080 for higher quality sharing. The captured image URI is stored in the `useShareCard` hook's state for immediate or deferred sharing. The capture can fail if the ref is not yet mounted — the hook handles this by checking `ref.current` before capture and throwing "Card view is not ready. Please try again." if the ref is null.

- `generateShareCard(ref, userId)`: captures at 720x1280, PNG, quality 1, temp file
- `generateHighResShareCard(ref)`: captures at 1080x1920, PNG, quality 1, temp file
- Validates `ref.current` is non-null before capture; throws if not ready
- `captureRef` options: `format: "png"`, `quality: 1`, `result: "tmpfile"`
- Output: temporary file URI on device (auto-cleaned by OS)
- Card must not be wrapped in a `Host` (SwiftUI) component — `react-native-view-shot` requires plain RN views

---

## 1.4 Social Share Integration

Once a card image is generated, the `shareCard(imageUri)` function presents the native share sheet via `expo-sharing`'s `shareAsync()`. The share sheet dialog title is "Share your FORGE progress". The MIME type is `image/png` with UTI `public.png`. For platform-specific sharing, `shareToSocial(imageUri, platform)` targets Instagram, TikTok, or Twitter with platform-appropriate dialog titles. Additionally, the `shareProgressReport(userId)` function generates a text-only progress summary and shares it via `Share.share()` as a fallback for platforms where image sharing isn't available. The `useShareCard` hook orchestrates the full flow: generate → share, with `isGenerating` and `isSharing` loading states, error handling, analytics events (`SHARE_CARD_GENERATED`, `SHARE_CARD_POSTED`), and optional XP award (50 XP, once per 24-hour cooldown tracked in AsyncStorage).

- `shareCard(imageUri)`: opens native share sheet via `shareAsync()` with "Share your FORGE progress" dialog
- `shareToSocial(imageUri, platform)`: platform-agnostic share with custom dialog titles per platform
- `shareProgressReport(userId)`: text-only fallback sharing via `Share.share()`
- `useShareCard` hook: `generate()` → `share()` flow with loading states, error handling, analytics
- `SHARE_CARD_GENERATED` event fired on successful card capture
- `SHARE_CARD_POSTED` event fired on successful share
- XP award: 50 XP for first share in a 24-hour window, tracked via AsyncStorage key `forge_last_share_xp_{userId}`
- Cooldown check: elapsed time >= 24 hours since last share XP award
