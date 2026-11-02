# Flutter Ansible Role

This role installs the Flutter SDK and its dependencies on Fedora Linux.

## What it Does

1. **Installs system dependencies** via DNF:
   - Development tools: git, curl, wget, clang, cmake, ninja-build
   - Graphics libraries: gtk3-devel, mesa-libGLU-devel
   - Compression tools: unzip, xz

2. **Installs Flutter SDK**:
   - Clones Flutter from GitHub to `~/.local/share/flutter`
   - Uses the stable channel by default
   - Runs `flutter precache --linux` to download platform binaries
   - Runs `flutter doctor` to verify installation

3. **Does NOT configure PATH** (that's handled by dotfiles)

## Installation

Run the full playbook:
```bash
make all
```

Or run just the Flutter role:
```bash
ansible-playbook -K -i hosts jupiter.yml --tags flutter
```

## Configuration Variables

Defined in `flutter/defaults/main.yml`:
- `flutter_channel`: stable (can be changed to beta, dev, or master)
- `flutter_install_dir`: `~/.local/share/flutter`
- `flutter_git_repo`: https://github.com/flutter/flutter.git

## Dotfiles Integration

The dotfiles repository configures Flutter with lazy loading in `bash/bashrc`:
- Adds Flutter to PATH only when `flutter` or `dart` commands are used
- Exports `FLUTTER_ROOT` environment variable
- Follows the same pattern as pyenv, rbenv, and nvm

## Post-Installation

After running Ansible and dotfiles, verify the installation:
```bash
source ~/.bashrc
flutter doctor
```

## Updating Flutter

To update Flutter to the latest version:
```bash
flutter upgrade
```

Or re-run the Ansible role to pull the latest from the git repository.

## Android Virtual Device (AVD)

This role also creates an Android emulator for testing:
- **AVD Name**: `flutter_emulator`
- **API Level**: 34 (Android 14)
- **Device Profile**: Pixel 7
- **System Image**: Google APIs (x86_64)

To launch the emulator:
```bash
flutter emulators --launch flutter_emulator
# or
emulator -avd flutter_emulator
```

To list available emulators:
```bash
flutter emulators
```

To customize the AVD, override variables in `jupiter.yml`:
```yaml
avd_name: my_custom_avd
avd_api_level: "33"
avd_device: "pixel_6"
```
