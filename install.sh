#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MOBILE_DIR="$SCRIPT_DIR/mobile"

usage() {
  cat <<EOF
FORGE Install Script
====================

Downloads and installs the latest EAS build onto a simulator/emulator.

Usage: ./install.sh <platform> [profile]

Platforms:
  ios           Install latest iOS build on the iOS Simulator
  android       Install latest Android build on the Android Emulator
  all           Install on both iOS Simulator and Android Emulator

Profiles:
  development   Dev client build (default)
  simulator     Simulator-specific build
  preview       Internal testing build

Examples:
  ./install.sh ios                    # Install latest iOS dev build
  ./install.sh android                # Install latest Android dev build
  ./install.sh ios simulator          # Install latest iOS simulator build
  ./install.sh all                    # Install on both platforms

EOF
  exit 0
}

[[ "$1" == "--help" || "$1" == "-h" || -z "$1" ]] && usage

PLATFORM="$1"
PROFILE="${2:-development}"

cd "$MOBILE_DIR"

if ! command -v eas &> /dev/null; then
  echo "EAS CLI not found. Installing..."
  npm install -g eas-cli
fi

install_ios() {
  echo "Installing latest iOS build (profile: $PROFILE) on Simulator..."
  eas build:run --platform ios --profile "$PROFILE"
}

install_android() {
  echo "Installing latest Android build (profile: $PROFILE) on Emulator..."
  eas build:run --platform android --profile "$PROFILE"
}

echo "=== FORGE Install ==="
echo "Platform: $PLATFORM"
echo "Profile:  $PROFILE"
echo ""

case "$PLATFORM" in
  ios)
    install_ios
    ;;
  android)
    install_android
    ;;
  all)
    install_ios
    echo ""
    install_android
    ;;
  *)
    echo "Error: Unknown platform '$PLATFORM'"
    echo "Run './install.sh --help' for usage."
    exit 1
    ;;
esac

echo ""
echo "Install complete."
