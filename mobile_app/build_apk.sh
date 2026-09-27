#!/bin/bash
# ==============================================================================
# EduManage ERP - 1-Click Android APK Build Script (macOS / Linux)
# ==============================================================================

set -e

echo "🚀 ==============================================="
echo "   EduManage ERP - Android APK Builder"
echo "==============================================="

# 1. Check if Flutter is installed
if ! command -v flutter &> /dev/null; then
    echo "❌ Error: Flutter SDK is not found in your PATH."
    echo "👉 Please install Flutter from: https://flutter.dev/docs/get-started/install"
    exit 1
fi

echo "✅ Flutter SDK detected: $(flutter --version | head -n 1)"

# 2. Get dependencies
echo "📦 Downloading Flutter packages (pub get)..."
flutter pub get

# 3. Clean previous builds
echo "🧹 Cleaning previous build artifacts..."
flutter clean
flutter pub get

# 4. Build Release APK
echo "⚙️ Building Release APK (Optimized for all Android devices)..."
flutter build apk --release --split-per-abi=false

APK_PATH="build/app/outputs/flutter-apk/app-release.apk"

if [ -f "$APK_PATH" ]; then
    echo ""
    echo "🎉 ==============================================="
    echo "   SUCCESS! APK Generated Successfully!"
    echo "==============================================="
    echo "📁 APK Location: $(pwd)/$APK_PATH"
    echo "📱 File Size: $(du -h "$APK_PATH" | cut -f1)"
    echo "📲 You can now copy this file to your Android phone and install it!"
    echo ""
else
    echo "❌ Build completed but APK was not found at expected path."
fi
