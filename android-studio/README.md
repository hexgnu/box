# Android Studio Role

Installs Android Studio via Flatpak and sets up the Android SDK for Flutter development.

## What it does

- Installs Android Studio via Flatpak
- Installs Java 17 (required for Android SDK tools)
- Downloads and installs Android command-line tools
- Automatically accepts SDK licenses
- Installs essential SDK components:
  - platform-tools (adb, fastboot)
  - Android 34 platform
  - Build tools 34.0.0
  - Android emulator
- Configures Flutter to use the Android SDK

## SDK Location

Android SDK is installed to: `~/Android/Sdk`

## Usage

After installation:
- `flutter doctor` should show Android toolchain as configured
- `adb` command is available in PATH (add `~/Android/Sdk/platform-tools` to PATH in dotfiles)
- Launch Android Studio: `flatpak run com.google.AndroidStudio`

## Environment Variables

Add to your dotfiles:
```bash
export ANDROID_SDK_ROOT=$HOME/Android/Sdk
export PATH=$ANDROID_SDK_ROOT/platform-tools:$ANDROID_SDK_ROOT/cmdline-tools/latest/bin:$PATH
```
