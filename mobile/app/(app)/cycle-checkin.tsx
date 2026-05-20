import { useState } from "react"
import {
  View,
  Text,
  StyleSheet,
  Pressable,
  ActivityIndicator,
  Alert,
  Image,
  Platform,
} from "react-native"
import { router } from "expo-router"
import * as ImagePicker from "expo-image-picker"
import { useSafeAreaInsets } from "react-native-safe-area-context"
import { Ionicons } from "@expo/vector-icons"
import { Colors, Spacing, Typography, Radius } from "@/constants/design"
import { useCycleStore } from "@/store/cycleStore"

type ScanMode = "face" | "full"

export default function CycleCheckinScreen() {
  const insets = useSafeAreaInsets()
  const { analysing, submitCheckin } = useCycleStore()
  const [photoUri, setPhotoUri] = useState<string | null>(null)
  const [scanMode, setScanMode] = useState<ScanMode>("face")

  const pickPhoto = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync()
    if (status !== "granted") {
      Alert.alert("Permission needed", "Gallery access is required to select a photo.")
      return
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ["images"],
      allowsEditing: true,
      aspect: scanMode === "face" ? [1, 1] : [3, 4],
      quality: 0.8,
    })

    if (!result.canceled && result.assets[0]) {
      setPhotoUri(result.assets[0].uri)
    }
  }

  const takePhoto = async () => {
    if (Platform.OS === "ios" || Platform.OS === "android") {
      const camResult = await ImagePicker.getCameraPermissionsAsync()
      if (!camResult.granted) {
        const { status } = await ImagePicker.requestCameraPermissionsAsync()
        if (status !== "granted") {
          Alert.alert("Permission needed", "Camera access is required to take a photo.")
          return
        }
      }

      try {
        const result = await ImagePicker.launchCameraAsync({
          allowsEditing: true,
          aspect: scanMode === "face" ? [1, 1] : [3, 4],
          quality: 0.8,
        })

        if (!result.canceled && result.assets[0]) {
          setPhotoUri(result.assets[0].uri)
        }
      } catch {
        Alert.alert(
          "Camera unavailable",
          "Camera is not available on this device. Please use the gallery instead."
        )
      }
    } else {
      Alert.alert("Not supported", "Camera is not available on web. Use gallery instead.")
    }
  }

  const handleSubmit = async () => {
    if (!photoUri) return

    try {
      const analysis = await submitCheckin(photoUri, scanMode)
      router.replace({
        pathname: "/(app)/cycle-result",
        params: { cycleId: analysis.cycle_id },
      })
    } catch (e: any) {
      Alert.alert("Analysis Failed", e.message || "Please try again later.")
    }
  }

  return (
    <View style={[styles.container, { paddingTop: insets.top + Spacing.lg }]}>
      <View style={styles.header}>
        <Pressable onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={24} color={Colors.bone} />
        </Pressable>
        <Text style={styles.title}>Cycle Check-in</Text>
        <View style={{ width: 40 }} />
      </View>

      <View style={styles.modeSelector}>
        <Pressable
          style={[styles.modeBtn, scanMode === "face" && styles.modeBtnActive]}
          onPress={() => setScanMode("face")}
        >
          <Text style={[styles.modeText, scanMode === "face" && styles.modeTextActive]}>
            Face Scan
          </Text>
        </Pressable>
        <Pressable
          style={[styles.modeBtn, scanMode === "full" && styles.modeBtnActive]}
          onPress={() => setScanMode("full")}
        >
          <Text style={[styles.modeText, scanMode === "full" && styles.modeTextActive]}>
            Full Scan
          </Text>
        </Pressable>
      </View>

      <View style={styles.photoArea}>
        {photoUri ? (
          <Image source={{ uri: photoUri }} style={styles.preview} />
        ) : (
          <View style={styles.placeholder}>
            <Ionicons name="camera-outline" size={48} color={Colors.ash} />
            <Text style={styles.placeholderText}>
              {scanMode === "face" ? "Take a front-facing photo" : "Take a full-body photo"}
            </Text>
          </View>
        )}
      </View>

      <View style={styles.actions}>
        <Pressable style={styles.actionBtn} onPress={takePhoto}>
          <Ionicons name="camera" size={22} color={Colors.bone} />
          <Text style={styles.actionText}>Camera</Text>
        </Pressable>
        <Pressable style={styles.actionBtn} onPress={pickPhoto}>
          <Ionicons name="images" size={22} color={Colors.bone} />
          <Text style={styles.actionText}>Gallery</Text>
        </Pressable>
      </View>

      <Pressable
        style={[styles.submitBtn, (!photoUri || analysing) && styles.submitBtnDisabled]}
        onPress={handleSubmit}
        disabled={!photoUri || analysing}
      >
        {analysing ? (
          <ActivityIndicator color={Colors.canvas} />
        ) : (
          <Text style={styles.submitText}>Analyse</Text>
        )}
      </Pressable>

      <Text style={styles.disclaimer}>
        Your photo is securely analysed and never shared. Results are used to personalise
        your program.
      </Text>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.canvas,
    paddingHorizontal: Spacing.screen,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: Spacing.xl,
  },
  backBtn: {
    width: 40,
    height: 40,
    justifyContent: "center",
    alignItems: "center",
  },
  title: {
    fontSize: Typography.sizes.heading,
    fontWeight: Typography.weights.bold,
    color: Colors.bone,
  },
  modeSelector: {
    flexDirection: "row",
    backgroundColor: Colors.raised,
    borderRadius: Radius.lg,
    padding: 3,
    marginBottom: Spacing.xl,
  },
  modeBtn: {
    flex: 1,
    paddingVertical: Spacing.md + 2,
    alignItems: "center",
    borderRadius: Radius.lg - 2,
  },
  modeBtnActive: {
    backgroundColor: Colors.ember,
  },
  modeText: {
    fontSize: Typography.sizes.caption,
    fontWeight: Typography.weights.medium,
    color: Colors.ash,
  },
  modeTextActive: {
    color: Colors.canvas,
  },
  photoArea: {
    flex: 1,
    borderRadius: Radius.card,
    overflow: "hidden",
    backgroundColor: Colors.raised,
    marginBottom: Spacing.lg,
  },
  preview: {
    width: "100%",
    height: "100%",
    resizeMode: "cover",
  },
  placeholder: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    gap: Spacing.md,
  },
  placeholderText: {
    fontSize: Typography.sizes.caption,
    color: Colors.ash,
    textAlign: "center",
  },
  actions: {
    flexDirection: "row",
    gap: Spacing.lg,
    justifyContent: "center",
    marginBottom: Spacing.xl,
  },
  actionBtn: {
    flexDirection: "row",
    alignItems: "center",
    gap: Spacing.md,
    backgroundColor: Colors.raised,
    paddingHorizontal: Spacing.xl,
    paddingVertical: Spacing.lg - 4,
    borderRadius: Radius.lg,
  },
  actionText: {
    fontSize: Typography.sizes.caption,
    fontWeight: Typography.weights.medium,
    color: Colors.bone,
  },
  submitBtn: {
    backgroundColor: Colors.ember,
    borderRadius: Radius.lg,
    paddingVertical: Spacing.lg,
    alignItems: "center",
    marginBottom: Spacing.lg,
  },
  submitBtnDisabled: {
    opacity: 0.4,
  },
  submitText: {
    fontSize: Typography.sizes.body,
    fontWeight: Typography.weights.bold,
    color: Colors.canvas,
  },
  disclaimer: {
    fontSize: Typography.sizes.label,
    color: Colors.muted,
    textAlign: "center",
    paddingBottom: Spacing.xl,
  },
})
