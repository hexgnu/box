# System Configuration TODOs

- [ ] Make a VPN work by turning on or off

## Fedora 39 → 42 Upgrade Critical Issues

### URGENT: Fix Hardcoded Version References
- [x] Update RPMFusion URLs in `jupiter.yml:39-47` from fc39 to fc42
- [x] Update RPMFusion URLs in `nvidia/tasks/main.yml:18,23` from fc39 to fc42
- [x] Parameterize Fedora version as a variable to avoid future hardcoding (set to 42)

### Repository Updates
- [x] Remove Docker CE in favor of Podman (Docker role disabled)
- [x] Add CUDA support for RTX 2080 Ti via RPMFusion packages

### NVIDIA/CUDA Configuration
- [x] Install CUDA toolkit and libraries from RPMFusion
- [x] Configure CUDA environment variables in /etc/profile.d/cuda.sh
- [x] Add nvidia-smi verification step
- [x] Install CUDA development tools (gcc-c++, cmake, python3-pycuda)
- [x] Create compatibility check script (check-fedora42-compatibility.sh)

### Testing NVIDIA Compatibility Before Upgrade
Run `./check-fedora42-compatibility.sh` to verify:
- RPMFusion repository availability for Fedora 42
- Current driver versions and compatibility
- Package availability checks

Alternative testing methods:
1. **Container testing** (safest):
   ```bash
   podman run -it --rm fedora:42 /bin/bash
   # Then check package availability inside container
   ```

2. **Check online resources**:
   - RPMFusion package database: https://admin.rpmfusion.org/pkgdb/package/nonfree/akmod-nvidia/
   - Koji build system: https://koji.rpmfusion.org/koji/packageinfo?packageID=13
   - Fedora 42 known issues: https://fedoraproject.org/wiki/Common_F42_bugs

3. **Virtual machine testing**:
   - Install Fedora 42 in a VM first
   - Test the ansible playbook there

4. **Check current driver support**:
   - RTX 2080 Ti requires minimum driver 410.xx
   - Current 550.xx drivers fully support it
   - CUDA capability 7.5 is well-supported

## Missing Package Management in Ansible

### Developer Tools
- [ ] Add VS Code installation
- [x] Add GitHub CLI (gh) - Added in developer-tools role
- [x] Add Azure CLI - Added in developer-tools role
- [x] Add Google Cloud CLI - Added in developer-tools role
- [x] Add Rust/Cargo - Added in developer-tools role with tools (ripgrep, fd-find, bat, exa, tokei)
- [x] Add hadolint - Added in developer-tools role (from GitHub releases)
- [x] Add httpie - Added in developer-tools role
- [x] Add GraphicsMagick - Added in developer-tools role with devel packages
- [x] Add pyenv - Created pyenv role with Python 3.11.9 and 3.12.4
- [x] Add nvm - Created nvm role with Node.js LTS
- [x] Remove rbenv - Replaced with pyenv for Python management

### System Utilities
- [ ] Add Snapd and manage Snap packages (or replace with native)
- [x] Add Podman and podman-compose - Created podman role with full Docker compatibility
- [ ] Add ClamAV antivirus with freshclam

## Flatpak Management
- [x] Flatpak role exists and manages:
  - [x] com.mastermindzh.tidal-hifi - Tidal music streaming client
  - [x] com.slack.Slack - Slack team communication (better than RPM method)

## System Services Not Managed
- [x] Configure Podman as Docker replacement - Full compatibility with docker commands

## Configuration Management Gaps
- [ ] Add systemd service enablement management
- [x] Manage NPM global packages via NVM:
  - [x] @anthropic-ai/claude-code - Installed in nvm role
  - [x] typescript, ts-node, nodemon, prettier, eslint, yarn, pnpm
- [ ] Add Podman container and volume management

## Infrastructure Improvements
- [ ] Create backup/restore role using the fedora-home-jupiter.home-* structure
- [ ] Add role for managing systemd services state
- [x] Add SSH key and GPG key management - Created keys role with smart generation/preservation

## Code Quality
- [x] Add tags to all tasks for selective execution - All roles now have proper tags
- [x] Add proper error handling for package installations - Added retries and until conditions
- [x] Create proper defaults and variable files - Created group_vars/all and role defaults
- [x] Add idempotency checks where missing - Used changed_when, creates, and state checks
- [ ] Document each role with README

## Improvements Completed
- **Makefile targets**: Added make nvidia, make dev, make desktop, make containers
- **Ansible.cfg**: Optimized for performance with fact caching and pipelining
- **Error handling**: All package installations now have retry logic
- **Variable management**: Centralized in group_vars/all/main.yml
- **Package state strategy**: Using 'present' for stability, 'latest' for CLI tools
- **Tags**: Can now run specific components with --tags
