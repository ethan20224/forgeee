import { useState } from "react"
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
} from "react-native"
import { useRouter, useLocalSearchParams } from "expo-router"
import { Colors, Typography, Spacing, Radius } from "@/constants/design"
import { useUserStore } from "@/store/userStore"
import * as authApi from "@/api/auth"
import { ApiRequestError } from "@/api/client"

export default function SignupScreen() {
  const router = useRouter()
  const params = useLocalSearchParams<{ mode?: string }>()
  const setUser = useUserStore((s) => s.setUser)
  const [mode, setMode] = useState<"signup" | "login">(
    params.mode === "login" ? "login" : "signup",
  )
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const isSignup = mode === "signup"

  function getHeadline() {
    return isSignup ? "Save your program." : "Welcome back."
  }

  function getSubline() {
    return isSignup
      ? "Your personalised plan is ready. Create an account to start."
      : "Log in to continue your programme."
  }

  function getButtonText() {
    return isSignup ? "Create account" : "Log in"
  }

  async function handleSubmit() {
    if (isSignup && (!name.trim() || !email.trim() || !password.trim())) {
      setError("All fields are required")
      return
    }
    if (!isSignup && (!email.trim() || !password.trim())) {
      setError("Email and password are required")
      return
    }
    if (isSignup && name.trim().length > 100) {
      setError("Name must be 100 characters or fewer")
      return
    }
    if (email.trim().length > 255) {
      setError("Email address is too long")
      return
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email.trim())) {
      setError("Please enter a valid email address")
      return
    }
    if (password.length < 8) {
      setError("Password must be at least 8 characters")
      return
    }
    if (password.length > 128) {
      setError("Password must be 128 characters or fewer")
      return
    }

    setLoading(true)
    setError(null)

    try {
      if (isSignup) {
        await authApi.signup(email.trim(), password, name.trim())
      } else {
        await authApi.login(email.trim(), password)
      }

      const user = await authApi.getMe()
      setUser(user)

      if (isSignup) {
        router.replace("/(auth)/plan-loading" as never)
      } else {
        if (user.onboarded) {
          router.replace("/(app)/(tabs)" as never)
        } else {
          router.replace("/(auth)/plan-loading" as never)
        }
      }
    } catch (err) {
      if (err instanceof ApiRequestError) {
        setError(err.message)
      } else {
        setError("Network error. Please try again.")
      }
    } finally {
      setLoading(false)
    }
  }

  function toggleMode() {
    setMode(isSignup ? "login" : "signup")
    setError(null)
  }

  return (
    <View style={styles.container}>
      <Text style={styles.headline}>{getHeadline()}</Text>
      <Text style={styles.subline}>{getSubline()}</Text>

      <View style={styles.form}>
        {isSignup && (
          <TextInput
            style={styles.input}
            placeholder="Name"
            placeholderTextColor={Colors.textTertiary}
            value={name}
            onChangeText={setName}
            autoCapitalize="words"
            editable={!loading}
            maxLength={100}
          />
        )}

        <TextInput
          style={styles.input}
          placeholder="Email"
          placeholderTextColor={Colors.textTertiary}
          value={email}
          onChangeText={setEmail}
          keyboardType="email-address"
          autoCapitalize="none"
          autoCorrect={false}
          editable={!loading}
          maxLength={255}
        />

        <TextInput
          style={styles.input}
          placeholder="Password"
          placeholderTextColor={Colors.textTertiary}
          value={password}
          onChangeText={setPassword}
          secureTextEntry
          autoCapitalize="none"
          editable={!loading}
          maxLength={128}
        />

        {error && <Text style={styles.error}>{error}</Text>}

        <TouchableOpacity
          style={[styles.button, loading && styles.buttonDisabled]}
          onPress={handleSubmit}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color={Colors.bg} />
          ) : (
            <Text style={styles.buttonText}>{getButtonText()}</Text>
          )}
        </TouchableOpacity>
      </View>

      <TouchableOpacity
        style={styles.toggleContainer}
        onPress={toggleMode}
        disabled={loading}
        activeOpacity={0.7}
      >
        <Text style={styles.toggleText}>
          {isSignup
            ? "Already have an account? "
            : "Don't have an account? "}
          <Text style={styles.toggleAction}>
            {isSignup ? "Log in" : "Sign up"}
          </Text>
        </Text>
      </TouchableOpacity>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.bg,
    paddingHorizontal: Spacing.screen,
    paddingTop: Spacing.xxxl,
  },
  headline: {
    color: Colors.textPrimary,
    fontSize: Typography.sizes.title,
    fontWeight: Typography.weights.bold,
    marginBottom: Spacing.md,
  },
  subline: {
    color: Colors.textSecond,
    fontSize: Typography.sizes.body,
    lineHeight: Typography.sizes.body * Typography.lineHeights.normal,
    marginBottom: Spacing.xxl,
  },
  form: {
    gap: Spacing.lg,
  },
  input: {
    backgroundColor: Colors.surface,
    borderWidth: 1,
    borderColor: Colors.border,
    borderRadius: Radius.md,
    paddingHorizontal: Spacing.lg,
    paddingVertical: Spacing.lg,
    color: Colors.textPrimary,
    fontSize: Typography.sizes.heading,
  },
  button: {
    backgroundColor: Colors.ember,
    borderRadius: Radius.md,
    paddingVertical: Spacing.lg,
    alignItems: "center",
    marginTop: Spacing.md,
  },
  buttonDisabled: {
    opacity: 0.5,
  },
  buttonText: {
    color: Colors.bg,
    fontSize: Typography.sizes.heading,
    fontWeight: Typography.weights.bold,
  },
  error: {
    color: Colors.danger,
    fontSize: Typography.sizes.body,
  },
  toggleContainer: {
    alignItems: "center",
    marginTop: Spacing.xxl,
  },
  toggleText: {
    fontSize: Typography.sizes.body,
    color: Colors.textSecond,
  },
  toggleAction: {
    fontSize: Typography.sizes.body,
    color: Colors.ember,
    fontWeight: Typography.weights.bold,
  },
})
