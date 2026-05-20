import { useState, useCallback, useEffect } from "react"
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  Pressable,
  StatusBar,
} from "react-native"
import { SafeAreaView } from "react-native-safe-area-context"
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withTiming,
} from "react-native-reanimated"
import { useLocalSearchParams, useRouter } from "expo-router"
import { Feather } from "@expo/vector-icons"
import { Colors } from "@/constants/design"
import { PrimaryButton } from "@/components/ui/PrimaryButton"
import { setCachedQuizAnswers } from "@/lib/quizCache"
import type { QuizSubmitRequest } from "@/types/api"

type QuestionType = "single" | "multi"

interface QuestionOption {
  id: string
  label: string
  value: string
}

interface QuestionDef {
  step: number
  question: string
  type: QuestionType
  answerKey: keyof QuizSubmitRequest
  options: QuestionOption[]
}

// Option values aligned to backend QuizSubmitRequest regex patterns
const QUESTIONS: QuestionDef[] = [
  {
    step: 1,
    question: "What do you want to improve most?",
    type: "multi",
    answerKey: "goals",
    options: [
      { id: "skin", label: "Skin", value: "skin" },
      { id: "grooming", label: "Grooming", value: "grooming" },
      { id: "hair", label: "Hair", value: "hair" },
      { id: "style", label: "Style", value: "style" },
      { id: "posture", label: "Frame & Posture", value: "posture" },
      { id: "sleep", label: "Sleep & Recovery", value: "sleep" },
      { id: "nutrition", label: "Nutrition", value: "nutrition" },
    ],
  },
  {
    step: 2,
    question: "What\u2019s your morning routine like right now?",
    type: "single",
    answerKey: "routine_level",
    options: [
      { id: "none", label: "I wash my face and that's it", value: "none" },
      {
        id: "basic",
        label: "I use a few products but nothing consistent",
        value: "basic",
      },
      {
        id: "moderate",
        label: "I have a routine and stick to it",
        value: "moderate",
      },
      {
        id: "advanced",
        label: "I\u2019m pretty advanced \u2014 I want to go further",
        value: "advanced",
      },
    ],
  },
  {
    step: 3,
    question:
      "How much time can you realistically spend on this every day?",
    type: "single",
    answerKey: "daily_time",
    options: [
      { id: "10min", label: "10 minutes", value: "10min" },
      { id: "20min", label: "20 minutes", value: "20min" },
      { id: "30min", label: "30 minutes", value: "30min" },
      { id: "45min", label: "45 minutes", value: "45min" },
      { id: "60min", label: "1 hour", value: "60min" },
    ],
  },
  {
    step: 4,
    question: "How serious is your appearance goal?",
    type: "single",
    answerKey: "timeline",
    options: [
      {
        id: "30days",
        label: "30 days \u2014 I want to see what\u2019s possible",
        value: "30days",
      },
      {
        id: "60days",
        label: "60 days \u2014 I want real momentum",
        value: "60days",
      },
      {
        id: "90days",
        label: "90 days \u2014 I want a complete transformation",
        value: "90days",
      },
    ],
  },
  {
    step: 5,
    question: "What do you most want to improve?",
    type: "single",
    answerKey: "main_concern",
    options: [
      { id: "skin", label: "Clearer skin", value: "skin" },
      { id: "grooming", label: "Better grooming", value: "grooming" },
      { id: "hair", label: "My hair", value: "hair" },
      { id: "style", label: "My style", value: "style" },
      { id: "posture", label: "My posture", value: "posture" },
      { id: "overall", label: "Overall improvement", value: "overall" },
    ],
  },
  {
    step: 6,
    question: "Your age range?",
    type: "single",
    answerKey: "age_range",
    options: [
      { id: "16-19", label: "16\u201319", value: "16-19" },
      { id: "20-24", label: "20\u201324", value: "20-24" },
      { id: "25-29", label: "25\u201329", value: "25-29" },
      { id: "30-34", label: "30\u201334", value: "30-34" },
      { id: "35-39", label: "35\u201339", value: "35-39" },
      { id: "40+", label: "40+", value: "40+" },
    ],
  },
]

const TOTAL = QUESTIONS.length

const quizCache: { answers: Partial<QuizSubmitRequest> } = { answers: {} }

function getCached(
  q: QuestionDef,
): string | string[] {
  const c = quizCache.answers[q.answerKey]
  if (q.type === "multi") return (c as string[] | undefined) ?? []
  return (c as string | undefined) ?? ""
}

function OptionItem({
  label,
  selected,
  onPress,
}: {
  label: string
  selected: boolean
  onPress: () => void
}) {
  const scale = useSharedValue(1)
  const animStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }))
  return (
    <Animated.View style={animStyle}>
      <Pressable
        style={[styles.option, selected && styles.optionSelected]}
        onPress={onPress}
        onPressIn={() => {
          scale.value = withTiming(0.98, { duration: 80 })
        }}
        onPressOut={() => {
          scale.value = withTiming(1, { duration: 100 })
        }}
      >
        <Text
          style={[
            styles.optionLabel,
            selected && styles.optionLabelActive,
          ]}
        >
          {label}
        </Text>
      </Pressable>
    </Animated.View>
  )
}

export default function QuizStep() {
  const { step } = useLocalSearchParams<{ step: string }>()
  const router = useRouter()
  const stepNum = parseInt(step ?? "1", 10)
  const question = QUESTIONS[stepNum - 1]

  const [selection, setSelection] = useState<string | string[]>(() =>
    question ? getCached(question) : "",
  )

  const isMulti = question?.type === "multi"

  const isSelected = useCallback(
    (value: string) =>
      isMulti
        ? (selection as string[]).includes(value)
        : selection === value,
    [selection, isMulti],
  )

  const handleSelect = useCallback(
    (value: string) => {
      if (isMulti) {
        setSelection((prev) => {
          const arr = prev as string[]
          return arr.includes(value)
            ? arr.filter((v) => v !== value)
            : [...arr, value]
        })
      } else {
        setSelection(value)
      }
    },
    [isMulti],
  )

  const canContinue = isMulti
    ? (selection as string[]).length > 0
    : typeof selection === "string" && selection.length > 0

  function handleContinue() {
    if (!question) return
    if (isMulti) {
      quizCache.answers.goals = selection as string[]
    } else {
      ;(quizCache.answers as Record<string, unknown>)[question.answerKey] =
        selection
    }

    if (stepNum < TOTAL) {
      router.push(`/(auth)/quiz/${stepNum + 1}` as never)
    } else {
      quizCache.answers.has_photo = false
      const finalAnswers = quizCache.answers as QuizSubmitRequest
      setCachedQuizAnswers(finalAnswers)
      router.replace("/(auth)/estimated-score" as never)
    }
  }

  if (!question) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>Invalid step.</Text>
      </View>
    )
  }

  const progressWidth = `${(stepNum / TOTAL) * 100}%` as `${number}%`

  return (
    <SafeAreaView style={styles.safe}>
      <StatusBar barStyle="light-content" backgroundColor={Colors.bg} />

      <View style={styles.progressTrack}>
        <Animated.View
          style={[styles.progressFill, { width: progressWidth }]}
        />
      </View>

      <View style={styles.header}>
        {stepNum > 1 ? (
          <Pressable
            onPress={() => router.back()}
            style={styles.backBtn}
            hitSlop={12}
          >
            <Feather
              name="arrow-left"
              size={20}
              color={Colors.textPrimary}
            />
          </Pressable>
        ) : (
          <View style={styles.backBtn} />
        )}
        <Text style={styles.stepCounter}>
          {stepNum} / {TOTAL}
        </Text>
      </View>

      <Text style={styles.question}>{question.question}</Text>

      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {question.options.map((opt) => (
          <OptionItem
            key={opt.id}
            label={opt.label}
            selected={isSelected(opt.value)}
            onPress={() => handleSelect(opt.value)}
          />
        ))}
      </ScrollView>

      <View style={styles.footer}>
        <PrimaryButton onPress={handleContinue} disabled={!canContinue}>
          {stepNum === TOTAL
            ? "Build my plan →"
            : "Continue →"}
        </PrimaryButton>
      </View>
    </SafeAreaView>
  )
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: Colors.bg },
  progressTrack: { height: 4, backgroundColor: Colors.textTertiary },
  progressFill: {
    height: 4,
    backgroundColor: Colors.ember,
    borderRadius: 999,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: 24,
    paddingTop: 16,
    paddingBottom: 8,
  },
  backBtn: {
    width: 32,
    height: 32,
    alignItems: "flex-start",
    justifyContent: "center",
  },
  stepCounter: {
    color: Colors.textTertiary,
    fontSize: 9,
    fontWeight: "700",
    letterSpacing: 1.2,
  },
  question: {
    color: Colors.textPrimary,
    fontSize: 17,
    fontWeight: "700",
    paddingHorizontal: 24,
    paddingBottom: 24,
    lineHeight: 17 * 1.3,
  },
  scroll: { flex: 1 },
  scrollContent: { paddingHorizontal: 24, paddingBottom: 120, gap: 10 },
  option: {
    minHeight: 56,
    backgroundColor: Colors.surface,
    borderWidth: 1,
    borderColor: Colors.border,
    borderRadius: 12,
    paddingHorizontal: 16,
    justifyContent: "center",
  },
  optionSelected: {
    backgroundColor: Colors.accentSubtle,
    borderColor: Colors.ember,
  },
  optionLabel: {
    fontSize: 13,
    fontWeight: "400",
    color: Colors.textPrimary,
  },
  optionLabelActive: { color: Colors.ember },
  footer: { paddingHorizontal: 24, paddingBottom: 24, paddingTop: 8 },
  errorContainer: {
    flex: 1,
    backgroundColor: Colors.bg,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 24,
  },
  errorText: {
    color: Colors.textSecond,
    fontSize: 13,
    textAlign: "center",
  },
})
