export type PhaseId = "foundation" | "activation" | "optimisation"

export const PHASE_DISPLAY: Record<
  PhaseId,
  { name: string; range: string; tagline: string }
> = {
  foundation: {
    name: "The Basics",
    range: "Days 1-28",
    tagline: "Core habits. Biggest visible wins first.",
  },
  activation: {
    name: "Building Up",
    range: "Days 29-56",
    tagline: "Adding products and routines that compound.",
  },
  optimisation: {
    name: "Results",
    range: "Days 57-90",
    tagline: "Everything compounds. This is when it shows.",
  },
}

export function phaseForDay(day: number): PhaseId {
  if (day <= 28) return "foundation"
  if (day <= 56) return "activation"
  return "optimisation"
}
