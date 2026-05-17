# Feature: Photo Management

> Capture, crop, compress, upload, and securely access user progress photos. Photos are stored in a private Supabase bucket with time-limited signed URLs for access.

Feature: Photo Management. Actor: User (Member). Phase: MVP.
Implementation: `src/services/image/imageService.ts`, `src/services/image/signedUrl.ts`, `supabase/migrations/010_private_photo_bucket.sql`
Purpose: Capture, crop, compress, upload, and securely access user progress photos. Photos are stored in a private Supabase bucket with time-limited signed URLs for access.

---

## 1.1 Camera Capture

The `imageService.ts` module provides photo capture via `expo-camera` for the cycle check-in screen. The capture flow supports up to three angles: front, left, and right (full scan mode). The camera screen shows a face guide overlay for consistent framing. After capture, each photo is stored locally at a temporary URI keyed by its `CaptureAngle` (`"front" | "left" | "right"`). The `CapturedPhoto` type carries `{ uri: string; angle: CaptureAngle }`. The user can retake any angle before proceeding to upload. The baseline photo capture (day 3) uses the same camera flow but captures only the front angle (face scan mode).

- Camera launched via `expo-camera` with face guide overlay for framing consistency
- Supports 3 angles: `front`, `left`, `right` (typed as `CaptureAngle`)
- Full scan mode captures all 3 angles; face scan mode captures front only
- `CapturedPhoto` type: `{ uri: string; angle: CaptureAngle }` — local temp URIs
- User can retake any angle before confirming upload
- Permission: camera permission requested inline with user-readable denial message
- Baseline photo capture (day 3) uses front angle only

---

## 1.2 Gallery Picker

Users can alternatively pick photos from their device library instead of using the camera. The `pickFromGallery()` function uses `expo-image-picker` to request media library permissions and launch the system picker. Photos are constrained to `aspect: [3, 4]` with `allowsEditing: true` for cropping. The quality is set to `0.8` — a balance between file size and visual fidelity. If the user cancels the picker, the function returns `null` (caller handles as no-op). If permissions are denied, a user-readable error is thrown: "Photo library permission denied. Please enable it in Settings."

- `pickFromGallery()` uses `expo-image-picker` with `mediaTypes: "images"`
- Permissions requested via `requestMediaLibraryPermissionsAsync()`, denied → error thrown
- Picker constrained: `aspect: [3, 4]`, `allowsEditing: true`, `quality: 0.8`
- User cancellation returns `null` (not an error — caller handles gracefully)
- Selected photo returned as local URI string

---

## 1.3 Image Processing (Crop 3:4, Compress ≤500KB, Mirror Flip)

The `cropAndCompressPortrait()` function processes a raw photo URI into a standardised format suitable for upload and AI analysis. Steps:

1. **Probe dimensions**: Read source width/height via `ImageManipulator.manipulateAsync` with no actions.
2. **Center crop to 3:4 portrait ratio**: Calculate target crop dimensions — crop to width = min(srcW, srcH * 3/4), center the crop rectangle.
3. **Resize**: Set width to 1080px (height auto-calculated from 3:4 ratio → 1440px).
4. **Mirror flip** (optional): If `flipHorizontal = true`, apply `ImageManipulator.FlipType.Horizontal` to correct front-camera mirroring.
5. **Compress to JPEG**: Apply `compress: 0.82` and `format: JPEG` — targets file sizes around 200–500KB for a typical portrait.

The function logs source dimensions, flip status, and partial URI at each step for debugging.

- Probe source dimensions with no-op `manipulateAsync` call
- Center crop: compute 3:4 target ratio, crop centered (origin = (srcW - cropW) / 2, (srcH - cropH) / 2)
- Resize to width 1080px (height derived from ratio: ~1440px)
- Optional horizontal flip for front-camera mirror correction (`FlipType.Horizontal`)
- Compress with `compress: 0.82`, format `JPEG` — targets ~200–500KB output
- Returns processed local URI
- Logs dimensions, flip flag, and URI prefix at each step

---

## 1.4 Upload to Private Bucket

Photos are uploaded to the `user-photos-private` Supabase storage bucket. The `uploadCyclePhotos()` function takes a `userId` and an array of `CapturedPhoto` objects, and uploads each one sequentially (to get clear per-angle error logs). Each photo is:

1. Fetched from its local URI as a Blob via `fetch(uri)`.
2. Validated: if the blob size is 0, an error is thrown.
3. Uploaded to `cycles/{userId}/{timestamp}-{angle}.jpg` via `supabase.storage.from(BUCKET).upload(path, blob, { contentType: "image/jpeg", upsert: false })`.
4. Returns an `UploadedImage` with `localUri` and `path`.

The upload is sequential (not parallel) to ensure clear error attribution — if photo 2 of 3 fails, the log clearly shows which angle failed. The bucket enforces a 10MB file size limit and restricts MIME types to `image/jpeg`, `image/jpg`, `image/png`, `image/webp`.

- Bucket: `user-photos-private` (private, RLS-protected)
- Upload path: `cycles/{userId}/{timestamp}-{angle}.jpg`
- Local URI fetched as Blob via `fetch()` → validated for non-zero size
- Uploaded with `contentType: "image/jpeg"`, `upsert: false`
- Sequential uploads for clear per-angle error attribution
- Returns `Record<CaptureAngle, UploadedImage>` keyed by angle
- `UploadedImage` type: `{ localUri: string; path: string }`
- Bucket limits: 10MB file size, MIME types: jpeg/jpg/png/webp

---

## 1.5 Signed URL Generation (3600s TTL, Cache)

Since the bucket is private, photo URLs must be generated on-demand with time-limited access. The `getSignedPhotoUrl()` function in `src/services/image/signedUrl.ts` calls `supabase.storage.from("user-photos-private").createSignedUrl(path, ttlSeconds)` with a default TTL of 300 seconds (5 minutes). On failure, it retries once before throwing a user-readable error. The `getSignedPhotoUrls()` function signs multiple paths in parallel via `Promise.all`. The signed URL system ensures:

1. URLs are only accessible for the duration of the user's session viewing photos.
2. Leaked URLs are useless after TTL expiry.
3. RLS ensures only the owning user can generate signed URLs for their photos (enforced at the bucket policy level).
4. The default TTL of 300s balances security (short window) with usability (user can browse their photo timeline without constant re-fetching).

For the photo timeline screen, signed URLs are cached in component state for the session duration and regenerated on mount or when the user pulls to refresh.

- `getSignedPhotoUrl(path, ttlSeconds = 300)`: single photo → signed URL
- Retry logic: on first failure, retries once; on second failure, returns user-readable error
- `getSignedPhotoUrls(paths[], ttlSeconds = 300)`: parallel signing via `Promise.all`
- Default TTL 300s (5 min) — balances security with UX
- Signed URLs cached in component state, regenerated on timeline refresh
- RLS policy: `Users can read their own photos private` enforces ownership at bucket level
- Errors: "Could not generate photo URL", "Photo URL not available", "Could not load photo"

---

## 1.6 Photo Timeline Display

The cycle check-in history is displayed as a scrollable photo timeline on the cycle/progress screens. The `getCyclePhotos()` function fetches all cycle records for a user from the `cycles` table ordered by `cycle_number DESC`. Each cycle record contains a `photo_path` (not a URL — the path is converted to a signed URL at display time). The timeline shows each cycle with its photo, FORGE score, date, and a delta indicator comparing to the previous cycle. The front photo is the primary display; left/right photos are accessible via a detail view.

- Cycle records fetched from `cycles` table ordered by `cycle_number DESC`
- `photo_path` stored in DB, converted to signed URL at render time via `getSignedPhotoUrl()`
- Timeline shows: photo thumbnail, cycle number, date, FORGE score, delta vs previous cycle
- Front photo is primary display; side photos accessible in detail view
- Baseline photo (cycle_number = 0 or cycle_type = "baseline") displayed with "Baseline" label
- Empty state: "No check-ins yet. Your first check-in is on day 3." with link to cycle screen
- Loading state: skeleton placeholder tiles matching photo aspect ratio
- Pull-to-refresh regenerates signed URLs for all visible photos

---

## 1.7 Photo Comparison (Side-by-Side, Delta Computation)

The before/after comparison feature allows users to select any two cycle photos and view them side-by-side with a draggable comparison slider. The comparison view overlays both signed photo URLs in a split-view container. Delta computation reads the pillar scores from both cycle records and displays the change for each of the 9 pillars as colored +/- indicators. The comparison supports: (a) baseline vs latest cycle, (b) any two arbitrary cycles selected from the timeline, (c) full scan comparison showing all 3 angles (front/left/right) in grids. The delta values drive the progress screen's pillar movement indicators and are referenced by the coaching engine for weekly report pillar analysis.

- Side-by-side photo display with draggable slider overlay for arbitrary cycle pair selection
- Delta computation: reads pillar scores from both cycle records, computes per-pillar difference
- Display: 9 pillar delta indicators with colored +/- (teal for positive, red for negative)
- Default comparison: baseline (cycle 0) vs latest cycle
- Full scan comparison: 3-angle grid view (front, left, right) for each cycle
- Delta values sourced from `cycles` table's per-pillar score columns
- Comparison result drives coaching language: "skin improved +3 since last check-in"
