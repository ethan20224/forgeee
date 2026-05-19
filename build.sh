#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MOBILE_DIR="$SCRIPT_DIR/mobile"

usage() {
  cat <<EOF
FORGE Build Script
==================

Usage: ./build.sh <platform> [profile]

Platforms:
  ios-sim       Build for iOS Simulator (local, no Apple account needed)
  ios           Build for iOS device (requires Apple Developer account)
  android       Build for Android (APK for testing)
  all           Build both iOS Simulator + Android

Profiles:
  development   Dev client with debugging (default)
  preview       Internal testing build
  production    App Store / Play Store release

Examples:
  ./build.sh ios-sim                  # iOS Simulator dev build (most common)
  ./build.sh ios-sim preview          # iOS Simulator preview build
  ./build.sh android                  # Android APK dev build
  ./build.sh ios production           # iOS App Store build
  ./build.sh all                      # Both platforms, dev profile

Options:
  --local       Run the build locally (no EAS cloud)
  --help        Show this help message

EOF
  exit 0
}

[[ "$1" == "--help" || "$1" == "-h" || -z "$1" ]] && usage

PLATFORM="$1"
PROFILE="${2:-development}"
LOCAL_FLAG=""

for arg in "$@"; do
  [[ "$arg" == "--local" ]] && LOCAL_FLAG="--local"
done

cd "$MOBILE_DIR"

# Ensure dependencies are installed
if [ ! -d "node_modules" ]; then
  echo "Installing dependencies..."
  npm install
fi

# Verify EAS CLI
if ! command -v eas &> /dev/null; then
  echo "EAS CLI not found. Installing..."
  npm install -g eas-cli
fi

echo "=== FORGE Build ==="
echo "Platform: $PLATFORM"
echo "Profile:  $PROFILE"
echo ""

case "$PLATFORM" in
  ios-sim)
    echo "Building iOS Simulator app..."
    eas build --platform ios --profile "${PROFILE}" $LOCAL_FLAG
    echo ""
    echo "After build completes:"
    echo "  1. Download the .app or .tar.gz from the build URL"
    echo "  2. Drag it onto the open Simulator window"
    echo "  OR if built locally, it installs automatically."
    ;;
  ios)
    echo "Building iOS device app..."
    echo "Note: Requires Apple Developer account configured in eas.json"
    eas build --platform ios --profile "${PROFILE}" $LOCAL_FLAG
    ;;
  android)
    echo "Building Android APK..."
    eas build --platform android --profile "${PROFILE}" $LOCAL_FLAG
    ;;
  all)
    echo "Building for all platforms..."
    eas build --platform all --profile "${PROFILE}" $LOCAL_FLAG
    ;;
  *)
    echo "Error: Unknown platform '$PLATFORM'"
    echo "Run './build.sh --help' for usage."
    exit 1
    ;;
esac

echo ""
echo "Build submitted. Check status at: https://expo.dev"
