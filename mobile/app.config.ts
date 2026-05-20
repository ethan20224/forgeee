import { ExpoConfig, ConfigContext } from "expo/config"

export default ({ config }: ConfigContext): ExpoConfig => ({
  ...config,
  name: "FORGE",
  slug: "forge",
  version: "1.0.0",
  orientation: "portrait",
  icon: "./assets/icon.png",
  userInterfaceStyle: "dark",
  newArchEnabled: true,
  scheme: "forge",
  splash: {
    image: "./assets/splash-icon.png",
    resizeMode: "contain",
    backgroundColor: "#0A0907",
  },
  ios: {
    supportsTablet: true,
    bundleIdentifier: "com.forge.app",
    infoPlist: {
      ITSAppUsesNonExemptEncryption: false,
      NSCameraUsageDescription: "FORGE needs camera access for cycle check-in photos.",
      NSPhotoLibraryUsageDescription: "FORGE needs gallery access to select check-in photos.",
    },
  },
  android: {
    adaptiveIcon: {
      foregroundImage: "./assets/adaptive-icon.png",
      backgroundColor: "#0A0907",
    },
    edgeToEdgeEnabled: true,
    package: "com.forge.app",
  },
  web: {
    favicon: "./assets/favicon.png",
    bundler: "metro",
    name: "FORGE — Male Appearance Optimisation",
    description: "Track, improve, and optimise your appearance with AI-powered analysis.",
    themeColor: "#0A0907",
    backgroundColor: "#0A0907",
  },
  plugins: [
    "expo-router",
    "expo-secure-store",
    [
      "expo-image-picker",
      {
        photosPermission: "FORGE needs gallery access to select check-in photos.",
        cameraPermission: "FORGE needs camera access for cycle check-in photos.",
      },
    ],
  ],
  extra: {
    router: {},
    eas: {
      projectId: "f9e52c44-77f4-471a-9b6f-4b116d0b0f36",
    },
  },
})
