# Box - Fedora Workstation Configuration

An Ansible-based system configuration repository for automating Fedora Linux workstation setup and management.

## Prerequisites

- Fedora Linux (tested on Fedora 39+)
- sudo privileges
- Git

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/hexgnu/box.git
   cd box
   ```

2. **Install dependencies**
   ```bash
   make depends
   ```
   This installs Ansible and Make if not already present.

3. **Run the configuration**
   ```bash
   make all
   ```
   You'll be prompted for your sudo password (BECOME password).

## Alternative Manual Setup

If you prefer to run commands manually:

1. **Install Ansible**
   ```bash
   sudo dnf install ansible
   ```

2. **Run the playbook directly**
   ```bash
   ansible-playbook -K -i hosts jupiter.yml -vvvv
   ```
   - `-K` prompts for sudo password
   - `-i hosts` specifies the inventory file
   - `-vvvv` provides verbose output for debugging

## What Gets Configured

This playbook sets up a complete development workstation including:

### Roles
- **keys**: SSH/GPG key management (runs first)
- **miniconda**: Python environment management via Conda
- **flatpak**: Flatpak application management
- **st**: Simple Terminal (suckless terminal emulator)
- **vim**: Vim editor configuration
- **pyenv**: Python version management
- **nvm**: Node Version Manager for Node.js
- **podman**: Container management (Docker alternative)
- **developer-tools**: Development utilities and tools
- **slack**: Slack desktop application
- **nvidia**: NVIDIA GPU drivers and configuration

### Additional Components
- **Desktop Environment**: i3 window manager, i3lock, i3status, dmenu
- **Development Libraries**: Various development libraries and compilers
- **System Utilities**: direnv, htop, tmux, awscli, and more
- **Fonts**: Source Code Pro, Font Awesome
- **Browsers**: Brave browser
- **Media**: VLC media player

## Post-Installation Steps

After running the Ansible playbook, complete setup manually:

### 1. Dotfiles Configuration

This playbook installs packages but does NOT configure your shell and applications automatically (to preserve your ability to customize).

To install dotfiles:
```bash
cd ~/git/personal/dotfiles
./bin/dotfiles
```

Or, to run dotfiles via Ansible:
```bash
ansible-playbook -K -i hosts jupiter.yml --tags dotfiles
```

### 2. Install Language Versions

Version managers are installed, but you choose which versions to use:

```bash
# Python (via pyenv)
pyenv install 3.12
pyenv global 3.12

# Node.js (via nvm)
nvm install --lts
nvm use --lts

# Ruby (via rbenv)
rbenv install 3.3.0
rbenv global 3.3.0
```

### 3. Verify Setup

```bash
# Check tools are available
which fzf zoxide eza bat fd delta lazygit
gh --version
git --version
tmux -V
nvim --version

# Check version managers
pyenv --version
nvm --version
rbenv --version
```

## Repository Relationship

This repository is part of a two-repo development environment setup:

- **box** (this repo): System provisioning and package installation
  - Installs packages via DNF
  - Manages system-level configuration
  - Requires sudo/root access
  - Run once per machine, occasionally for updates

- **dotfiles** (~/git/personal/dotfiles): User configuration and preferences
  - Configures shell, editor, git, tmux, i3, etc.
  - User-owned files and symlinks
  - No sudo required
  - Updated frequently, version controlled

**Boundary:** Ansible handles system setup (root), dotfiles handles user config (no sudo).

See dotfiles repo at: https://github.com/hexgnu/dotfiles

## Customization

The main configuration is in `jupiter.yml`. Key variables you may want to modify:
- `username`: Your system username (default: hexgnu)
- `hostname`: Your machine hostname (default: jupiter.home)
- `email`: Your email address (default: matt@matthewkirk.com)
- `fedora_version`: Target Fedora version (default: 42)
- `ssh_keygen_bits`: SSH key size (default: 4096)
- `ssh_keygen_types`: SSH key types (default: ed25519)

## Troubleshooting

- If the playbook fails, you can re-run it - Ansible tasks are idempotent
- For detailed debugging, use the `-vvvv` flag with ansible-playbook
- Check individual role tasks in their respective `tasks/main.yml` files

## GitHub Credentials Setup

After running the playbook, configure your GitHub credentials:
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```
