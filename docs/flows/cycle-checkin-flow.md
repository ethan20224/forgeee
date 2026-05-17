# Flow: Cycle Check-In

> 3-day photo check-in flow: capture → upload → AI analysis → results → timeline.

Flow: Cycle Check-In. Actor: User. Trigger: Day 3, 6, 9... or notification tap. End state: New cycle analysis saved with scores + insights.

---

## Happy Path

```
1. Trigger: User taps cycle notification ("Cycle photo today.") OR navigates to cycle tab from home
   └─> Cycle eligibility check (useCycles hook)
       ├─ Check baseline photo exists? (users.baseline_photo_path)
       │   └─ If no baseline → redirect to baseline-photo screen (day 3 prompt)
       │       ├─ Camera opens with face guide overlay
       │       ├─ User takes front photo → crop/compress/upload
       │       ├─ Baseline saved to users (baseline_photo_path, baseline_photo_url via signed URL)
       │       ├─ AI analysis runs → returns initial pillar scores + face shape
       │       └─ Navigate back to cycle check-in
       ├─ Check if can check in now? (daysUntilNextCycle ≤ 0 or first check-in)
       │   └─ If not yet → show "Next check-in in {N} days" with countdown
       └─> User taps "Start Check-In"
           └─> Scan mode selection (face vs full)
               ├─ Face mode: 1 photo (front only — excludes style/sleep/nutrition/voice from analysis)
               └─ Full mode: 3 photos (front, left, right — all 9 pillars analysed)
                   └─> Camera opens (expo-camera)
                       ├─ Face guide overlay displayed for consistent framing
                       ├─ For full mode: sequential capture with on-screen instructions
                       │   ├─ Step 1: "Front — face the camera directly"
                       │   ├─ Step 2: "Left — turn your head to the left"
                       │   └─ Step 3: "Right — turn your head to the right"
                       └─> After capture: preview screen
                           ├─ User can review each photo
                           ├─ "Retake" button per angle
                           └─ "Continue" button
                               └─> Image processing (per photo)
                                   ├─ cropAndCompressPortrait(uri, flipHorizontal)
                                   │   ├─ Center crop to 3:4 portrait ratio
                                   │   ├─ Resize to 1080px width
                                   │   ├─ Mirror flip (front camera correction)
                                   │   └─ Compress JPEG quality 0.82 (~200-500KB)
                                   └─> Upload to Supabase private bucket
                                       ├─ uploadCyclePhotos(userId, photos)
                                       │   ├─ Fetch blob from local URI
                                       │   ├─ Upload to cycles/{userId}/{timestamp}-{angle}.jpg
                                       │   └─ Return UploadedImage per angle (path, localUri)
                                       ├─ saveCycleRecord(userId, uploadedPhotos)
                                       │   ├─ Insert into cycles table (photo_path, cycle_type)
                                       │   └─ cycle_number auto-assigned by DB trigger
                                       └─> Generate signed URLs
                                           ├─ getSignedPhotoUrl(path, 300) per photo path
                                           └─> Send to Codex Vision for analysis
                                               ├─ callClaudeVision(imageUrls, systemPrompt)
                                               │   ├─ Model: Claude Sonnet 4.6
                                               │   ├─ Vision mode: URL-based (not base64)
                                               │   └─ Returns structured CycleAnalysis JSON
                                               └─> Analysis received
                                                   ├─ Validation: all expected pillar scores present?
                                                   │   └─ Missing scores → set to null, flag in analysis
                                                   ├─ Apply scan mode filters (face mode → exclude style/sleep/nutrition/voice)
                                                   ├─ Update progress table with new pillar scores
                                                   ├─ Recalculate optimisation_score via scoreCalculator
                                                   ├─ Update cycle record with analysis results
                                                   └─> Display results screen
                                                       ├─ "Check-in Complete!" header
                                                       ├─ FORGE Score (large, animated, with delta vs previous)
                                                       ├─ "Top Movers" — pillars with biggest positive deltas
                                                       ├─ AI insight (primary insight from analysis)
                                                       ├─ "Next Focus" — recommended pillar for upcoming days
                                                       ├─ Per-pillar score breakdown (9 bars)
                                                       └─ "View Timeline" → navigate to photo timeline
```

---

## Alternate Paths

### Pick from Gallery
```
User on cycle screen → taps "Pick from Gallery" instead of camera
├─ pickFromGallery() → system photo library picker
│   ├─ Permission check: media library access
│   ├─ Picker configured: aspect [3:4], allowsEditing true, quality 0.8
│   └─ Returns local URI or null (cancelled)
├─ Selected photo goes through same processing pipeline (crop/compress/upload)
├─ Full scan from gallery: user picks 3 photos sequentially
└─ Analysis continues identically after upload
```

### Full Scan Mode (3 Photos)
```
User selects "Full Scan" on check-in screen
├─ Camera opens 3 times sequentially with angle instructions
├─ All 3 photos processed and uploaded
├─ 3 signed URLs passed to Codex Vision
├─ Analysis includes all 9 pillars
│   ├─ Face-specific: facial_composition, skin, grooming, hair
│   ├─ Posture: analysed from full-body context in side photos
│   ├─ Style: analysed from outfit in photos
│   ├─ Sleep: inferred from under-eye appearance
│   ├─ Nutrition: inferred from skin clarity and face composition
│   └─ Voice: not analysable from photos → set to null in face mode, data_gap in full mode
└─ Side photos stored in cycle record's ai_insight as JSON metadata
```

### Retake Photo
```
After capture → preview screen → user taps "Retake" on an angle
├─ Discard current photo for that angle (no upload)
├─ Return to camera for that specific angle
├─ Re-capture → new preview → confirm or retake again
└─ All angles must be confirmed before processing begins
```

### Baseline Check-In (Cycle 0)
```
User on day 3 → prompted to take baseline photo
├─ cycle_type = "baseline", cycle_number = 0
├─ Front photo only (face scan mode)
├─ Analysis returns: initial pillar scores, face shape detection
├─ face_shape saved to users table
├─ Pillar weights adjusted based on detected face shape
├─ Baseline photo path saved to users.baseline_photo_path
├─ Onboarding compliment generated: generateOnboardingCompliment(bestPillar)
└─ Displayed with celebration: "Your journey begins. Baseline score: {score}"
```

---

## Error States

| Error | Detection | User Experience |
|-------|-----------|-----------------|
| **No baseline photo** | `users.baseline_photo_path` is null AND `cycle_type !== "baseline"` | Redirect to baseline photo screen: "Take your baseline photo first to unlock progress tracking." Cannot proceed with check-in until baseline exists. |
| **Photo too dark / poor quality** | Codex Vision returns `photo_quality_flag: "poor"` or low confidence scores | Analysis proceeds with available data. Results screen shows a warning banner: "Photo quality was low. For best results, use good lighting and a clear angle." Scores may have lower confidence. |
| **Codex Vision timeout** | `callClaudeVision()` exceeds 30s timeout | Processing screen shows "Analysis taking longer than expected..." after 20s. After 30s: "Our AI is still processing. You can close the app — we'll notify you when your results are ready." Analysis continues server-side; results saved to cycle record when complete. Push notification fires when ready. |
| **Upload failure** | `uploadCyclePhotos()` or individual blob upload fails | Processing screen shows which angle failed: "Could not upload your {front/left/right} photo. Please try again." with "Retry" button. Previously uploaded photos preserved — only failed angle needs re-upload. |
| **Missing pillar scores in analysis** | CycleAnalysis JSON missing expected score fields | Missing scores set to null in the cycle record. Progress table updated only for pillars with valid scores. Results screen: missing pillars shown as "—" with "Not available this check-in" tooltip. Analysis retry attempted via `retryPhotoAnalysis()` edge function. |
