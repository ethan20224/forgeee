export type Pillar =
  | "skin"
  | "grooming"
  | "hair"
  | "posture"
  | "style"
  | "sleep"
  | "facial_composition"
  | "nutrition"
  | "voice"

export const VISIBLE_PILLARS: Pillar[] = [
  "skin",
  "grooming",
  "hair",
  "posture",
  "style",
  "sleep",
]

export const PILLAR_DISPLAY: Record<
  Pillar,
  { plain: string; brand: string }
> = {
  skin: { plain: "Skin", brand: "Clarity" },
  grooming: { plain: "Grooming", brand: "Sharpness" },
  hair: { plain: "Hair", brand: "Density" },
  posture: { plain: "Posture & Body", brand: "Frame" },
  style: { plain: "Style", brand: "Presentation" },
  sleep: { plain: "Sleep & Recovery", brand: "Recovery" },
  facial_composition: { plain: "Facial", brand: "Composition" },
  nutrition: { plain: "Nutrition", brand: "Fuel" },
  voice: { plain: "Voice", brand: "Voice" },
}

export function pillarDisplayName(p: Pillar, seasonDay: number): string {
  return seasonDay >= 91
    ? PILLAR_DISPLAY[p].brand
    : PILLAR_DISPLAY[p].plain
}
