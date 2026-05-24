# FORGE Landing Page — Animation Brief for Google Stitch

## Platform & Tech Stack

- **Framework**: React Native (Expo Router)
- **Animation library**: `react-native-reanimated` (v3+)
- **Screen dimensions**: Full-screen mobile view (iPhone/Android)
- **Background**: Solid `#0A0907` (near-black)

---

## Current Layout (Static)

The screen has two sections stacked vertically:

### 1. Hero (center of screen)
- A **circular glow** — 240×240px circle, color `rgba(212,165,116,0.12)`, absolutely positioned behind text
- **Wordmark** — "FORGE" in bold white (`#F0ECE4`), 32px, letter-spacing 2.2px
- **Tagline** — "Your appearance. Measured. Improved." in muted color (`#8A7E72`), 13px

### 2. Actions (bottom of screen)
- **Primary button** — Full-width pill (border-radius 999), solid amber/ember fill (`#D4A574`), text "Create my program →" in dark
- **Secondary button** — Full-width pill, 1px border `rgba(212,165,116,0.20)`, dim fill `rgba(212,165,116,0.12)`, text "I already have an account" in amber

---

## Desired Animations

### A. Glow Pulse (Ambient — loops forever)

| Property | Detail |
|----------|--------|
| Target | The 240px circular glow behind the wordmark |
| Effect | Slow scale pulse between 1.0 → 1.15 → 1.0, with subtle opacity shift 0.12 → 0.18 → 0.12 |
| Duration | 3–4 seconds per cycle |
| Easing | Smooth sine / ease-in-out |
| Loop | Infinite, continuous |
| Purpose | Creates a "breathing" warmth behind the logo — premium, alive feel |

### B. Wordmark Fade-In (On mount — once)

| Property | Detail |
|----------|--------|
| Target | "FORGE" text |
| Effect | Fade in from opacity 0 → 1, slight upward translate (y: +10 → 0) |
| Duration | 600ms |
| Delay | 200ms after screen mounts |
| Easing | `Easing.out(Easing.cubic)` |

### C. Tagline Fade-In (On mount — once)

| Property | Detail |
|----------|--------|
| Target | Tagline text |
| Effect | Fade in from opacity 0 → 1, slight upward translate (y: +8 → 0) |
| Duration | 500ms |
| Delay | 500ms (staggered after wordmark) |
| Easing | `Easing.out(Easing.cubic)` |

### D. Buttons Slide-Up (On mount — once)

| Property | Detail |
|----------|--------|
| Target | Both buttons (the actions container) |
| Effect | Slide up from y: +30 → 0, opacity 0 → 1 |
| Duration | 500ms |
| Delay | 700ms (staggered after tagline) |
| Easing | `Easing.out(Easing.cubic)` |

### E. Button Press Scale (On interaction)

| Property | Detail |
|----------|--------|
| Target | Whichever button is pressed |
| Effect | Scale down to 0.96 on press-in, spring back to 1.0 on press-out |
| Duration | 80ms press-in, 120ms release |
| Easing | `withTiming` or `withSpring` (light spring, damping: 15) |

---

## Animation Sequence Timeline

```
0ms       200ms      500ms      700ms      1200ms     ∞
|----------|----------|----------|----------|----------|----->
           Wordmark   Tagline    Buttons    All idle   Glow pulses
           fades in   fades in   slide up              continuously
```

---

## Design Tokens Reference

```
Colors:
  bg:           #0A0907
  ember:        #D4A574
  emberDim:     rgba(212,165,116,0.12)
  emberBorder:  rgba(212,165,116,0.20)
  textPrimary:  #F0ECE4
  textSecond:   #8A7E72
  canvas:       #0A0907

Typography:
  wordmark:  32px, weight 700, letter-spacing 2.2px
  tagline:   13px, weight 400, letter-spacing 0.44px
  button:    13px, weight 700

Spacing:
  screen padding: 24px horizontal
  bottom padding: 48px
  gap between buttons: 12px
  gap between wordmark and tagline: 16px

Radii:
  buttons: 999 (full pill)
  glow circle: 120 (half of 240)
```

---

## Constraints

- Use `react-native-reanimated` shared values and `useAnimatedStyle`
- All animations should run on the UI thread (worklets)
- No Lottie or external animation files — purely code-driven
- The glow pulse must not impact layout (use `transform: scale` only)
- Entrance animations should only play once (not on re-render or back-navigation)
- Keep total JS bundle impact minimal

---

## Mood / Feel

Premium, minimal, confident. Think luxury fitness app meets fintech onboarding. The glow should feel like embers breathing — warm and alive but never distracting. Entrance animations should feel swift and purposeful, not playful or bouncy.
