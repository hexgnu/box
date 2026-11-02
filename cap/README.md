# Cap Ansible Role

Installs [Cap](https://cap.so) (`Cap`), an open source screen recorder and Loom
alternative.

## What it Does

1. **Installs the `cap` RPM** from upstream's official Fedora build. Cap is
   **not on Flathub** and not in the Fedora repos, so this follows the same
   download-and-install pattern as the `zoom` role.
2. **Lets `dnf` resolve the runtime dependencies** (`pipewire-libs`,
   `vulkan-loader`, `libva`, `libxkbcommon-x11`, `pulseaudio-utils`, …) from the
   Fedora repos — they are all packaged, so none are listed explicitly.
3. **Does NOT configure Cap** — app settings and any login state belong to the
   user's home directory, not here.

Installed binaries: `/usr/bin/Cap` (the GUI, note the capital C),
`/usr/bin/cap-cli`, `/usr/bin/cap-muxer`. Desktop entry:
`/usr/share/applications/Cap.desktop`.

## Installation

```bash
make cap         # this role only
make all         # full playbook
```

## Upgrading

Bump `cap_version` in `defaults/main.yml` and rerun `make cap`.

Unlike most roles here, `cap_version` is **not a pin**. Upstream distributes
only a "latest" redirect (`https://cap.so/download/linux-rpm` →
`cdn.crabnebula.app`); there is no versioned URL, and the GitHub releases carry
no RPM assets. So `cap_version` records *what you expect to be installed*, and a
mismatch against the installed RPM is what triggers a reinstall from the latest
URL.

Consequence worth knowing: if you set `cap_version` lower than what the CDN
currently serves, the role reinstalls on every run and never converges. The
verify task prints the actual installed version alongside a hint when the two
disagree, so this surfaces on the first run rather than silently.

## Variables

| Variable            | Default                             | Description                          |
|---------------------|-------------------------------------|--------------------------------------|
| `cap_version`       | `0.6.1`                             | Expected installed version (not a pin) |
| `cap_package_name`  | `cap`                               | RPM name used for the `rpm -q` check |
| `cap_rpm_url`       | `https://cap.so/download/linux-rpm` | Upstream "latest RPM" redirect       |
| `cap_rpm_tmp_path`  | `/tmp/cap-latest.rpm`               | Download staging path                |
| `cap_min_glibc`     | `2.39`                              | Upstream minimum (informational)     |

## Usage Notes

- The RPM is **unsigned** (no `SIGPGP`/`SIGGPG` header), so the install runs
  with `disable_gpg_check: yes`. Same as the `zoom` and direct-download `slack`
  paths in this repo.
- The download is ~99MB, so it is fetched only when an install is actually
  going to happen — the cheap `rpm -q` check gates it, which is why the role is
  safe to carry the `quick` tag.
- Upstream requires glibc ≥ 2.39. Fedora 42 ships 2.41, so this box is fine;
  Ubuntu 22.04-era systems are not supported even via the AppImage.
