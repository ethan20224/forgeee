import { StyleSheet, Pressable, Text, type ViewStyle } from "react-native"
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withTiming,
} from "react-native-reanimated"
import { Colors } from "@/constants/design"

interface PrimaryButtonProps {
  children: React.ReactNode
  onPress?: () => void
  disabled?: boolean
  style?: ViewStyle
}

export function PrimaryButton({
  children,
  onPress,
  disabled,
  style,
}: PrimaryButtonProps) {
  const scale = useSharedValue(1)
  const animStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }))

  return (
    <Animated.View
      style={[styles.outer, disabled && styles.disabled, style, animStyle]}
    >
      <Pressable
        style={styles.inner}
        onPress={disabled ? undefined : onPress}
        onPressIn={() => {
          if (!disabled) scale.value = withTiming(0.97, { duration: 80 })
        }}
        onPressOut={() => {
          scale.value = withTiming(1, { duration: 100 })
        }}
        disabled={disabled}
      >
        <Text style={styles.text}>{children}</Text>
      </Pressable>
    </Animated.View>
  )
}

const styles = StyleSheet.create({
  outer: {
    width: "100%",
    height: 52,
    borderRadius: 999,
    backgroundColor: Colors.ember,
    overflow: "hidden",
  },
  disabled: { backgroundColor: Colors.emberDim, opacity: 0.6 },
  inner: { flex: 1, alignItems: "center", justifyContent: "center" },
  text: { color: Colors.canvas, fontSize: 13, fontWeight: "700" },
})
