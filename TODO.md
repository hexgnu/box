# System Configuration TODOs

## Existing Tasks
- [ ] Install nordvpn: https://support.nordvpn.com/Connectivity/Linux/1325529112/Installing-and-using-NordVPN-on-Fedora-and-QubesOS-Linux.htm#Settings

## Fedora 39 → 42 Upgrade Critical Issues

### URGENT: Fix Hardcoded Version References
- [x] Update RPMFusion URLs in `jupiter.yml:39-47` from fc39 to fc42
- [x] Update RPMFusion URLs in `nvidia/tasks/main.yml:18,23` from fc39 to fc42
- [x] Parameterize Fedora version as a variable to avoid future hardcoding (set to 42)

### Repository Updates
- [x] Remove Docker CE in favor of Podman (Docker role disabled)
- [x] Add CUDA support for RTX 2080 Ti via RPMFusion packages
- [ ] Test nvidia driver compatibility with Fedora 42
- [ ] Verify all third-party repos work with Fedora 42

### NVIDIA/CUDA Configuration
- [x] Install CUDA toolkit and libraries from RPMFusion
- [x] Configure CUDA environment variables in /etc/profile.d/cuda.sh
- [x] Add nvidia-smi verification step
- [x] Install CUDA development tools (gcc-c++, cmake, python3-pycuda)

## Missing Package Management in Ansible

### Developer Tools
- [ ] Add VS Code installation
- [ ] Add GitHub CLI (gh)
- [ ] Add GitLab CLI (glab)
- [ ] Add Azure CLI
- [ ] Add Google Cloud CLI
- [ ] Add MongoDB tools (mongosh, mongodb-database-tools)
- [ ] Add Redis server
- [ ] Add PostgreSQL server (currently only has devel libs)
- [ ] Add Golang
- [ ] Add Rust/Cargo
- [ ] Add hadolint
- [ ] Add httpie
- [ ] Add orb CLI
- [ ] Add graphicsmagick
- [ ] Add various development libraries (cairo-devel, gtk3-devel, etc.)

### System Utilities
- [ ] Add Tailscale VPN configuration
- [ ] Add Snapd and manage Snap packages (or replace with native)
- [ ] Add Podman and podman-compose (PRIMARY - replaces Docker)
- [ ] Add ClamAV antivirus with freshclam
- [ ] Add smartmontools
- [ ] Add sysstat
- [ ] Add spamassassin
- [ ] Add stress-ng
- [ ] Add testdisk
- [ ] Add qpdf
- [ ] Add speedtest-cli
- [ ] Add inxi system info tool

### Desktop Applications
- [ ] Add Lutris gaming platform
- [ ] Add SimpleScreenRecorder
- [ ] Add Filezilla
- [ ] Add Weechat IRC client
- [ ] Add GIMP image editor
- [ ] Add Protonmail Bridge
- [ ] Add Rescuetime tracker
- [ ] Add pavucontrol audio control
- [ ] Add Betterbird email client

### Games
- [ ] Add SuperTuxKart
- [ ] Add ExtremeTuxRacer
- [ ] Add DOSBox-staging
- [ ] Add Wine/Winetricks
- [ ] Add Cmatrix

## Missing Flatpak Management
- [ ] Create Flatpak role to manage:
  - [ ] app.ytmdesktop.ytmdesktop
  - [ ] com.mastermindzh.tidal-hifi
  - [ ] com.usebruno.Bruno
  - [ ] eu.betterbird.Betterbird

## System Services Not Managed
- [ ] Add Ollama AI service management
- [ ] Add Orb service management
- [ ] Configure Podman as Docker replacement
- [ ] Add PCP monitoring services configuration
- [ ] Add libvirt/QEMU virtual machine services

## Configuration Management Gaps
- [ ] Add systemd service enablement management
- [ ] Manage NPM global packages:
  - [ ] @anthropic-ai/claude-code
  - [ ] claude
  - [ ] cspell
- [ ] Manage Cargo packages:
  - [ ] tod time tracker
- [ ] Add Podman container and volume management

## Infrastructure Improvements
- [ ] Create backup/restore role using the fedora-home-jupiter.home-* structure
- [ ] Add role for managing systemd services state
- [ ] Create role for firewall configuration
- [ ] Add SSH key and GPG key management (currently in backup but not Ansible)
- [ ] Add NetworkManager connections restore
- [ ] Add printer configuration management

## Testing & Validation
- [ ] Test full playbook on fresh Fedora 42 install
- [ ] Verify all packages exist in Fedora 42 repos
- [ ] Check for deprecated packages and find replacements
- [ ] Test nvidia driver installation on Fedora 42
- [ ] Validate all systemd services start correctly

## Code Quality
- [ ] Add tags to all tasks for selective execution
- [ ] Add proper error handling for package installations
- [ ] Create proper defaults and variable files
- [ ] Add idempotency checks where missing
- [ ] Document each role with README
