@echo off
REM ==============================================================================
REM EduManage ERP - 1-Click Android APK Build Script (Windows)
REM ==============================================================================

echo 🚀 ===============================================
echo    EduManage ERP - Android APK Builder (Windows)
echo ===============================================

where flutter >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Error: Flutter SDK is not found in your PATH.
    echo 👉 Please install Flutter from: https://flutter.dev/docs/get-started/install
    pause
    exit /b 1
)

echo ✅ Flutter SDK detected.
echo 📦 Downloading Flutter packages...
call flutter pub get

echo 🧹 Cleaning build cache...
call flutter clean
call flutter pub get

echo ⚙️ Building Release APK...
call flutter build apk --release

if exist "build\app\outputs\flutter-apk\app-release.apk" (
    echo.
    echo 🎉 ===============================================
    echo    SUCCESS! APK Generated Successfully!
    echo ===============================================
    echo 📁 APK Location: %cd%\build\app\outputs\flutter-apk\app-release.apk
    echo 📲 You can now copy this file to your phone and install it!
    echo.
) else (
    echo ❌ Build failed or APK not found.
)

pause
