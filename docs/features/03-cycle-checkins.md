# Feature: Cycle Check-Ins

**Actor:** User (Member)
**Phase:** MVP ✅ Done
**Related flows:** [cycle-checkin-flow.md](../flows/cycle-checkin-flow.md), [onboarding-flow.md](../flows/onboarding-flow.md)
**Implementation:** `app/(app)/cycle.tsx`, `app/(app)/photo-compare.tsx`, `app/(app)/photo-timeline.tsx`, `src/hooks/useCycles.ts`, `src/hooks/useCycleHistory.ts`, `src/hooks/usePhotoTimeline.ts`, `src/services/ai/photoAnalyser.ts`, `src/services/image/imageService.ts`

## Purpose

Every 3 days, the user takes progress photos. Codex Vision (Claude) analyses them against the 9 pillars, providing objective scores, insights, and focus areas. Results are stored for historical comparison, allowing the user to see objective improvement over the 90-day season.

## Data Model

Cycles are stored in the `cycles` Supabase table:

| Column | Type | Description |
|--------|------|-------------|
| `id` | uuid | Primary key |
| `user_id` | uuid | FK to users |
| `cycle_number` | integer | Auto-incremented (trigger) — 0 for baseline, 1+ for check-ins |
| `cycle_type` | text | `baseline` or `checkin` |
| `photo_url` | text | Public URL (populated by trigger/signed URL at display time) |
| `photo_path` | text | Private bucket path: `cycles/{userId}/{timestamp}-front.jpg` |
| `checked_in_at` | timestamptz | When cycle was created |
| `face_shape` | text | Detected face shape from AI analysis |
| `ai_insight` | jsonb | Full AI analysis JSON + side photo paths |
| `next_focus` | text | AI-recommended focus area for next 3 days |
| `facial_composition_score` through `voice_score` | integer | 9 individual pillar scores (0-100) |

Photo storage: `user-photos-private` bucket, path pattern `cycles/{userId}/{timestamp}-{angle}.jpg`.

---

## Subsections

### 3.1 Check-In Eligibility

**Implementation:** `useCycles` hook — `canCheckInNow` and `daysUntilNextCycle` computed values.

**Logic:**
- `plan_start_date` is the user's program start date (set during onboarding).
- **First check-in:** If `cycles` table has no records, user is eligible when `daysSinceStart >= 3`. This means the baseline photo prompt on day 3 triggers the first cycle.
- **Subsequent check-ins:** Find most recent cycle's `checked_in_at`. User is eligible when `daysSinceLast >= 3`.
- `daysUntilNextCycle`: number of days until next eligible date. 0 if `canCheckInNow` is true.
- Baseline photo gate: `useBaselineStatus` hook checks if `users.baseline_photo_path` is set. If not, cycle check-in is blocked and user is redirected to `app/(app)/baseline-photo.tsx`.

**UI Indicators:**
- Home screen tile/card: shows "Next check-in in {daysUntilNextCycle} days" or "Check-in available now" with teal highlight.
- Cycle tab/screen: "Check In Now" button enabled when `canCheckInNow` is true, disabled with countdown otherwise.

**Edge Cases:**
- If `plan_start_date` is null → `canCheckInNow = false` (user may have skipped onboarding DB write).
- If latest cycle date is in the future (clock skew) → treat as not eligible.
- Timezone-aware: date comparisons use local date (`YYYY-MM-DD` in user's timezone).

**Acceptance Criteria:**
- AC-1.1: First check-in eligible exactly 3 days after `plan_start_date`.
- AC-1.2: Subsequent check-ins eligible exactly 3 days after previous cycle.
- AC-1.3: `daysUntilNextCycle` displays correct countdown.
- AC-1.4: "Check In Now" button disabled when not eligible.
- AC-1.5: No baseline photo → cycle screen redirects to baseline-photo.
- AC-1.6: Null `plan_start_date` safely returns `canCheckInNow = false`.

---

### 3.2 Photo Capture

**Screen:** `app/(app)/cycle.tsx`

Camera interface for capturing progress photos with face alignment guidance.

**Camera Setup:**
- Uses `expo-camera` with front camera default.
- Face guide overlay (`FaceGuideOverlay` component): semi-transparent oval outline indicating where the user's face should be positioned. Matches the 3:4 portrait crop area.
- `LightingIndicator` component: shows ambient light quality (good/low) based on brightness sensor or estimated from camera frame.
- Scan mode selector (segmented control):
  - **"Face" mode:** Single front photo. For quick check-ins focused on facial pillars (facial_composition, skin, grooming, hair).
  - **"Full" mode:** Front + left + right photos. For comprehensive body posture, style analysis. Requires 3 captures.

**Capture Flow:**
1. User selects scan mode (default: "face").
2. User positions face within guide overlay.
3. User taps capture button (large circular button, centre-bottom).
4. Photo preview appears with "Retake" and "Use Photo" options.
5. If "full" mode, repeats for left and right angles.
6. Photos stored in local state as array of `{ uri: string, angle: CaptureAngle }`.

**Alternative: Gallery Pick:**
- "Choose from Library" link below capture button.
- Calls `pickFromGallery()` → opens device photo library with 3:4 aspect ratio crop.
- Single photo only from gallery (can only be used in "face" mode).

**States:** Camera loading (permission request), camera active, photo preview, gallery pick.

**Acceptance Criteria:**
- AC-2.1: Front camera opens with face guide overlay.
- AC-2.2: "Face" mode captures one photo; "Full" mode captures three.
- AC-2.3: Photo preview allows retake or confirm.
- AC-2.4: Gallery picker opens with 3:4 aspect ratio constraint.
- AC-2.5: Camera permissions requested on first use with clear explanation.
- AC-2.6: Permission denied shows settings redirect message.
- AC-2.7: Lighting indicator reflects actual ambient conditions.
- AC-2.8: Scan mode persists selection across sessions (local state only).

---

### 3.3 Image Processing

**Implementation:** `imageService.cropAndCompressPortrait(uri, flipHorizontal)`

**Processing Pipeline (per photo):**
1. **Crop to 3:4 portrait ratio:** Computes centre crop of source image to 3:4 aspect ratio. If source is wider than 3:4, crops width. If taller, crops height. Ensures consistent framing across all cycles.
2. **Resize:** Target width 1080px (maintains aspect ratio). Ensures files are reasonable size for upload and AI analysis.
3. **Flip horizontally:** Applied when `flipHorizontal = true` (front camera photos only). Corrects the mirror effect from front-facing cameras.
4. **Compress:** JPEG format at 82% quality. Target file size ≤ 500KB. Actual compressed size may vary — quality setting is tuned to hit ≤ 500KB for most 1080px portraits.

**Processing Rules:**
- Front camera photos: always flip horizontal (mirror correction).
- Gallery/library photos: no flip (already correctly oriented).
- Left/right photos: no flip (rear camera, or front with correct orientation).

**Acceptance Criteria:**
- AC-3.1: Photos cropped to centred 3:4 portrait ratio.
- AC-3.2: Output width is 1080px.
- AC-3.3: Front camera photos flipped horizontally.
- AC-3.4: Gallery photos not flipped.
- AC-3.5: Output file size ≤ 500KB at 82% JPEG quality.
- AC-3.6: Processing does not distort aspect ratio.

---

### 3.4 Photo Upload

**Implementation:** `imageService.uploadAndSaveCycle(userId, photos)` → `uploadCyclePhotos` + `saveCycleRecord`

**Upload Pipeline:**
1. For each photo in `CapturedPhoto[]`, call `uploadPhotoBlob(userId, uri, suffix, timestamp)`:
   - Fetch local file as blob via `fetch(uri)`.
   - Validate blob is non-empty (throws if 0 bytes).
   - Upload to `user-photos-private/{cycles}/{userId}/{timestamp}-{angle}.jpg`.
   - Content-Type: `image/jpeg`.
   - Returns `UploadedImage { localUri, path }`.
2. Uploads are sequential (one at a time) for clearer error reporting.
3. After all uploads complete, call `saveCycleRecord(userId, uploadedPhotos)`:
   - Inserts row into `cycles` table with `photo_path = frontPath`, `ai_insight` as JSON containing side photo paths (`{ side_photos: { left, right } }`).
   - `cycle_number` auto-assigned by PostgreSQL trigger `trg_assign_cycle_number`.
   - Returns `CycleRecord { id, photo_url, photo_path, cycle_number, checked_in_at }`.

**Signed URL Generation:**
- After upload, generate signed URL via `getSignedPhotoUrl(path)` for Claude Vision analysis.
- Signed URLs expire after 3600 seconds (1 hour) — sufficient for the AI analysis call.
- Uses Supabase Storage signed URL API.

**Upload Error Handling:**
- Network failure: retry once automatically. On second failure, show error "Upload failed — check your connection and try again."
- Storage quota exceeded: specific error message "Photo storage full. Contact support."
- Empty blob: "Could not read photo file — please retake."

**Acceptance Criteria:**
- AC-4.1: Photo uploaded to correct bucket path (`cycles/{userId}/`).
- AC-4.2: Cycle record created in database with auto-incremented `cycle_number`.
- AC-4.3: Side photo paths stored in `ai_insight` JSON.
- AC-4.4: Signed URL generated and valid for ≥ 1 hour.
- AC-4.5: Upload errors throw user-readable messages.
- AC-4.6: Empty blob detection prevents invalid uploads.
- AC-4.7: `PHOTO_UPLOADED` PostHog event fires on successful upload.
- AC-4.8: Baseline upload also sets `users.baseline_photo_path`.

---

### 3.5 AI Analysis

**Implementation:** `photoAnalyser.analysePhotos(photoUrls, cycleNumber, scanMode, cycleType?, previousScores?, faceShape?)`

**Pipeline:**
1. Build user message via `buildPhotoUserMessage({ cycleNumber, date, previousScores, habitData, faceShape, photoAngles })`.
2. Call `callClaudeVision(PHOTO_ANALYSIS_SYSTEM_PROMPT, imageUrls, userMessage)` via `claude-proxy` edge function.
3. Parse JSON response, strip markdown fences if present.
4. Validate response structure: must contain `cycle_number`, `date`, `photo_quality_flag`, `pillar_scores` (9 keys), `forge_score`, `primary_insight`, `next_focus`. All 9 pillar keys must be objects.
5. Apply scan mode filters:
   - **"face" mode:** Set `style` to `data_gap`, `sleep` to `data_gap`, `nutrition` to `data_gap`, `voice` to `null`. These pillars cannot be assessed from face-only photos.
   - **"full" mode:** No filtering — all pillars assessed.
6. Clamp all scores: pillar scores 0-100, deltas -100 to +100. Ensure `forge_score.cycle_high` is not below `forge_score.current`.
7. Return clamped, validated `CycleAnalysis`.

**AI Simulation Mode:**
- When `EXPO_PUBLIC_AI_SIMULATION=true`: returns `MOCK_CYCLE_ANALYSIS` with simulated scores after 1.5s delay. Used for development.
- Controlled by `src/config/aiSimulation.ts`.

**Response Validation:**
- If JSON parse fails: throw "AI returned an invalid response. Please try again."
- If structure validation fails: throw "AI analysis was incomplete. Please try again."
- Both are user-facing errors with implicit retry (user taps "Try Again" on cycle screen).

**Error States:**
- Rate limited (429 from claude-proxy): "Too many requests. Please wait and try again."
- AI timeout: "Analysis took too long. Your photos are saved — we'll retry automatically."
- Generic failure: "Could not analyse your photos. Please retry."

**Acceptance Criteria:**
- AC-5.1: Claude Vision analyses photos and returns valid JSON.
- AC-5.2: All 9 pillar scores present in response.
- AC-5.3: "Face" mode filters out style, sleep, nutrition, voice pillars.
- AC-5.4: "Full" mode returns all 9 pillars.
- AC-5.5: Scores clamped to 0-100 range.
- AC-5.6: `forge_score.cycle_high` never below `forge_score.current`.
- AC-5.7: Invalid JSON response throws user-readable error.
- AC-5.8: Invalid structure response throws user-readable error.
- AC-5.9: AI simulation mode returns mock data when enabled.
- AC-5.10: Rate limit errors display appropriate message.

---

### 3.6 Result Display

**Component:** `CycleResultCard` in `src/components/ui/CycleResultCard.tsx`

**Display:**
- **FORGE Score:** Large animated number, teal coloured (`#00C4A7`). Shows `forge_score.current`. Below it: a smaller delta indicator (+2 or -1 vs last cycle).
- **Per-Pillar Scores:** Horizontal scrollable list of 9 pillar score cards. Each card:
  - Pillar name (from `PILLAR_DISPLAY`).
  - Score (0-100) with coloured progress bar.
  - Delta indicator (green up arrow for positive, no indicator for null/negative).
  - `data_gap` pillars shown with muted "No data" label.
  - `null` pillars hidden entirely.
- **Primary Insight:** 1-2 sentence AI insight displayed in a prominent quote-style card. Italic, secondary text colour.
- **Next Focus:** "Focus for next 3 days: {next_focus}" — displayed as a coaching tip card with teal left border.
- **Photo Quality Flag:** If `photo_quality_flag` is "poor" or "needs_retake", a warning banner appears: "Photo quality may affect accuracy — try better lighting next time."

**Save to Database:**
- `updateCycleWithAnalysis(cycleId, userId, analysis)` merges the `CycleAnalysis` JSON into the existing `ai_insight` JSON (preserving side photo paths).
- Populates all 9 pillar score columns on the `cycles` row.
- Sets `face_shape`, `next_focus`.
- `CYCLE_COMPLETED` PostHog event fires with `{ cycle_number, optimisation_score }`.

**Acceptance Criteria:**
- AC-6.1: FORGE Score displayed as large teal number with animation.
- AC-6.2: Per-pillar scores scrollable with coloured progress bars.
- AC-6.3: `data_gap` pillars shown as muted "No data".
- AC-6.4: `null` pillars hidden from display.
- AC-6.5: Primary insight displayed in quote card.
- AC-6.6: Next focus displayed as coaching tip.
- AC-6.7: Photo quality warning shown for "poor" or "needs_retake".
- AC-6.8: Analysis saved to cycle row in database.
- AC-6.9: `CYCLE_COMPLETED` event fires with correct properties.

---

### 3.7 Photo Timeline

**Screen:** `app/(app)/photo-timeline.tsx`

Scrollable chronological history of all cycle photos with key metrics.

**Display:**
- Vertical scrollable list, most recent first.
- Each entry shows:
  - Cycle number badge (top-left).
  - Date string ("Mar 15" format).
  - Thumbnail photo (square, rounded corners). Signed URL generated on-demand via `getSignedPhotoUrl`.
  - FORGE Score (teal number).
  - Top pillar (pillar with highest score, coloured dot + name).
  - AI insight preview (truncated to 1 line).
- Tapping an entry navigates to that cycle's detail view or opens `CycleComparisonModal`.

**Before/After Comparison:**
- "Compare" button in timeline header.
- Tapping opens `CycleComparisonModal`:
  - Select two cycle entries (default: baseline vs latest).
  - Side-by-side photo display.
  - Score delta table: shows pillar, baseline score, current score, delta.
  - Biggest mover highlighted in teal.
  - "Share Comparison" button → generates share card.

**Empty State:**
- "No photos yet" with camera icon.
- "Your first check-in is in {daysUntilNextCycle} days" if before day 3.
- "Take your first photo" CTA → navigates to baseline-photo or cycle screen.

**Loading:**
- Skeleton list with 5 placeholder entries (rounded photo + text lines).

**Acceptance Criteria:**
- AC-7.1: Timeline shows all cycles in reverse chronological order.
- AC-7.2: Each entry displays photo, score, top pillar, date correctly.
- AC-7.3: Tapping entry navigates to detail/comparison.
- AC-7.4: Compare feature shows side-by-side photos with score deltas.
- AC-7.5: Empty state shown when no cycles exist.
- AC-7.6: Signed URLs generated on-demand for photo display.
- AC-7.7: Skeleton loading shown during fetch.

---

### 3.8 Notifications

**Implementation:** `src/services/notifications/notificationService.ts`
**Schedule:** Every 3 days at 10:00 AM local time.

**Cycle Prompt Notification:**
- Title: "Cycle photo today."
- Body: "Same angle, same lighting."
- Category: `cycle_reminder` (iOS notification category).
- Deep link: tapping opens `/(app)/cycle`.
- Language: factual, non-guilting. No urgency, no FOMO, no "don't miss your check-in".
- Scheduled via `expo-notifications` with `scheduleNotificationAsync`.
- Re-scheduled after each check-in: cancels next pending cycle notification, schedules new one for +3 days.

**Notification Behaviour:**
- Requests notification permissions during onboarding (after paywall success).
- If permissions denied: shows in-app banner on home screen when check-in is available.
- Badge count: updates app icon badge to show days since last check-in (resets to 0 on check-in).

**Acceptance Criteria:**
- AC-8.1: Cycle notification fires every 3 days at 10am local time.
- AC-8.2: Notification uses factual language: "Cycle photo today. Same angle, same lighting."
- AC-8.3: Tapping notification opens cycle screen.
- AC-8.4: Notification re-scheduled after each check-in.
- AC-8.5: In-app banner shown when notification permissions denied.
- AC-8.6: No guilt language in notification body.
