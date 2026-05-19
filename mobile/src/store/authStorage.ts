import * as SecureStore from "expo-secure-store"
import { Platform } from "react-native"

const ACCESS_KEY = "forge_access_token"
const REFRESH_KEY = "forge_refresh_token"

function isSecureStoreAvailable(): boolean {
  return Platform.OS !== "web"
}

export async function saveTokens(
  accessToken: string,
  refreshToken: string,
): Promise<void> {
  if (isSecureStoreAvailable()) {
    await SecureStore.setItemAsync(ACCESS_KEY, accessToken)
    await SecureStore.setItemAsync(REFRESH_KEY, refreshToken)
  } else {
    localStorage.setItem(ACCESS_KEY, accessToken)
    localStorage.setItem(REFRESH_KEY, refreshToken)
  }
}

export async function getTokens(): Promise<{
  accessToken: string | null
  refreshToken: string | null
}> {
  if (isSecureStoreAvailable()) {
    const accessToken = await SecureStore.getItemAsync(ACCESS_KEY)
    const refreshToken = await SecureStore.getItemAsync(REFRESH_KEY)
    return { accessToken, refreshToken }
  }
  return {
    accessToken: localStorage.getItem(ACCESS_KEY),
    refreshToken: localStorage.getItem(REFRESH_KEY),
  }
}

export async function clearTokens(): Promise<void> {
  if (isSecureStoreAvailable()) {
    await SecureStore.deleteItemAsync(ACCESS_KEY)
    await SecureStore.deleteItemAsync(REFRESH_KEY)
  } else {
    localStorage.removeItem(ACCESS_KEY)
    localStorage.removeItem(REFRESH_KEY)
  }
}
