export const Colors = {
  canvas: "#0A0907",
  surface: "#0E0D0B",
  raised: "#161412",
  raisedHi: "#1C1916",
  divider: "rgba(255,255,255,0.06)",

  bone: "#F0ECE4",
  ash: "#8A7E72",
  muted: "#5C544A",
  boneTint: "#E8DFD0",

  ember: "#D4A574",
  emberDim: "rgba(212,165,116,0.12)",
  emberBorder: "rgba(212,165,116,0.20)",

  brass: "#D4A574",

  bg: "#0A0907",
  elevated: "#161412",
  border: "rgba(255,255,255,0.06)",
  borderMed: "rgba(255,255,255,0.10)",
  teal: "#D4A574",
  tealDim: "rgba(212,165,116,0.12)",
  tealBorder: "rgba(212,165,116,0.20)",
  gold: "#D4A574",
  goldDim: "rgba(212,165,116,0.12)",
  goldBorder: "rgba(212,165,116,0.20)",
  textPrimary: "#F0ECE4",
  textSecond: "#8A7E72",
  textTertiary: "#5C544A",
  danger: "#E84545",
  dangerDim: "rgba(232,69,69,0.12)",

  checkDone: "#5A6B4F",
  checkDoneDim: "rgba(90,107,79,0.20)",

  accentSubtle: "rgba(212,165,116,0.05)",
  accentSurface: "rgba(212,165,116,0.04)",
  accentBorderStrong: "rgba(212,165,116,0.30)",

  facial: "#D4A574",
  facialDim: "rgba(212,165,116,0.12)",
  skin: "#D4A574",
  skinDim: "rgba(212,165,116,0.12)",
  grooming: "#D4A574",
  groomingDim: "rgba(212,165,116,0.12)",
  hair: "#D4A574",
  hairDim: "rgba(212,165,116,0.12)",
  posture: "#D4A574",
  postureDim: "rgba(212,165,116,0.12)",
  style: "#D4A574",
  styleDim: "rgba(212,165,116,0.12)",
  sleep: "#D4A574",
  sleepDim: "rgba(212,165,116,0.12)",
  nutrition: "#D4A574",
  nutritionDim: "rgba(212,165,116,0.12)",
  voice: "#D4A574",
  voiceDim: "rgba(212,165,116,0.12)",
  lifestyle: "#D4A574",
  lifestyleDim: "rgba(212,165,116,0.12)",

  iconOnLight: "#1A1208",
  transparent: "transparent",
} as const

export const Typography = {
  sizes: {
    mega: 80,
    hero: 64,
    display: 32,
    title: 24,
    heading: 17,
    body: 17,
    caption: 13,
    label: 11,
    micro: 11,
    nano: 9,
  },
  weights: {
    light: "300" as const,
    regular: "400" as const,
    medium: "500" as const,
    bold: "700" as const,
    extraBold: "800" as const,
  },
  lineHeights: {
    tight: 1.1,
    normal: 1.55,
    relaxed: 1.6,
  },
  letterSpacing: {
    tightest: -3.0,
    tight: -2.2,
    snug: -0.64,
    normal: 0,
    wide: 0.44,
    wider: 1.8,
    widest: 2.2,
  },
  font: "Inter",
} as const

export const Spacing = {
  xs: 2,
  sm: 4,
  md: 8,
  lg: 16,
  xl: 24,
  xxl: 32,
  xxxl: 48,
  screen: 24,
} as const

export const Radius = {
  none: 0,
  sm: 2,
  md: 4,
  lg: 8,
  card: 12,
  xl: 20,
  full: 999,
} as const

export const Animation = {
  fast: 150,
  normal: 250,
  slow: 400,
  spring: 350,
} as const

export const Easing = {
  entrance: "cubic-bezier(0.16, 1, 0.3, 1)",
  resolution: "cubic-bezier(0.4, 0, 1, 1)",
  state: "cubic-bezier(0.4, 0, 0.2, 1)",
} as const
