import { Platform } from "react-native"
import { getTokens, saveTokens, clearTokens } from "@/store/authStorage"

const DEFAULT_HOST = Platform.OS === "android" ? "10.0.2.2" : "localhost"
const BASE_URL =
  process.env.EXPO_PUBLIC_API_URL ?? `http://${DEFAULT_HOST}:8000/api/v1`

let isRefreshing = false
let refreshPromise: Promise<boolean> | null = null

async function attemptRefresh(): Promise<boolean> {
  const { refreshToken } = await getTokens()
  if (!refreshToken) return false

  try {
    const resp = await fetch(`${BASE_URL}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    })
    if (!resp.ok) {
      await clearTokens()
      return false
    }
    const data = await resp.json()
    await saveTokens(data.access_token, data.refresh_token)
    return true
  } catch {
    await clearTokens()
    return false
  }
}

async function refreshOnce(): Promise<boolean> {
  if (isRefreshing && refreshPromise) return refreshPromise
  isRefreshing = true
  refreshPromise = attemptRefresh().finally(() => {
    isRefreshing = false
    refreshPromise = null
  })
  return refreshPromise
}

async function buildHeaders(
  extra?: Record<string, string>,
): Promise<Record<string, string>> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...extra,
  }
  const { accessToken } = await getTokens()
  if (accessToken) {
    headers["Authorization"] = `Bearer ${accessToken}`
  }
  return headers
}

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
  skipAuth = false,
): Promise<T> {
  const url = `${BASE_URL}${path}`
  const headers = skipAuth
    ? { "Content-Type": "application/json" }
    : await buildHeaders()

  let resp = await fetch(url, {
    method,
    headers,
    body: body != null ? JSON.stringify(body) : undefined,
  })

  if (resp.status === 401 && !skipAuth) {
    const refreshed = await refreshOnce()
    if (refreshed) {
      const retryHeaders = await buildHeaders()
      resp = await fetch(url, {
        method,
        headers: retryHeaders,
        body: body != null ? JSON.stringify(body) : undefined,
      })
    }
  }

  if (!resp.ok) {
    const errorBody = await resp.json().catch(() => ({ detail: resp.statusText }))
    throw new ApiRequestError(
      errorBody.detail ?? "Request failed",
      resp.status,
      errorBody,
    )
  }

  if (resp.status === 204) return undefined as T
  return resp.json()
}

export class ApiRequestError extends Error {
  status: number
  body: unknown

  constructor(message: string, status: number, body?: unknown) {
    super(message)
    this.name = "ApiRequestError"
    this.status = status
    this.body = body
  }
}

export const api = {
  get: <T>(path: string) => request<T>("GET", path),
  post: <T>(path: string, body?: unknown) => request<T>("POST", path, body),
  patch: <T>(path: string, body?: unknown) => request<T>("PATCH", path, body),
  del: <T>(path: string) => request<T>("DELETE", path),
  postPublic: <T>(path: string, body?: unknown) =>
    request<T>("POST", path, body, true),
}
