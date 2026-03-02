# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Ansible-based system configuration repository for managing Fedora Linux workstation setups. The repository automates the installation and configuration of development tools, applications, and system settings for a machine named "jupiter.home".

## Core Commands

### Running the Ansible Playbook
```bash
# Install dependencies
make depends  # Installs ansible and make

# Run the full configuration
make all  # Runs ansible-playbook with jupiter.yml playbook
# Or directly:
ansible-playbook -K -i hosts jupiter.yml -vvvv
```

## Architecture

### Ansible Structure
- **Main Playbook**: `jupiter.yml` - Orchestrates all roles and tasks for system configuration
- **Inventory**: `hosts` - Defines target hosts (currently localhost as 127.0.0.1)
- **Configuration**: `ansible.cfg` - Ansible settings with Python 3 interpreter and SSH pipelining

### Role Organization
Each component is organized as an Ansible role under its own directory with a `tasks/main.yml` file:
- **Development Tools**: `vim/`, `rbenv/`, `miniconda/`, `docker/`
- **Desktop Environment**: `i3/`, `i3blocks/`, `dmenu/`, `st/` (terminal)
- **Applications**: `slack/`, `zoom/`, `flatpak/`
- **System**: `nvidia/` (GPU drivers), `postgres/`, `ssh/`
- **Utilities**: `authoring/`, `direnv/`, `install_repos/`

### Key Variables (defined in jupiter.yml)
- `username`: hexgnu
- `hostname`: jupiter.home
- `email`: matt@matthewkirk.com
- `ansible_python_interpreter`: /usr/bin/python3

### System Backup Directory
`fedora-home-jupiter.home-20250817/` contains system configuration backups including:
- Package lists (rpm, flatpak, pip, npm)
- System configurations (i3, cron, systemd)
- SSH and GPG keys
- Network configurations

## Development Notes

- The playbook uses `become: true` with sudo for privilege escalation
- RPMFusion repositories (free and non-free) are configured for additional packages
- Dotfiles are managed via a separate repository at github.com/hexgnu/dotfiles
- The system includes both native package management (DNF) and Flatpak for application installation

## Repository Relationship

This repository is part of a two-repo development environment setup:

### Box Repository (This Repo)
**Purpose:** System provisioning and package installation
**Responsibilities:**
- Install packages via DNF (system package manager)
- Add third-party repositories (RPMFusion, Azure CLI, GCloud)
- Install language version managers (pyenv, nvm, rbenv - the tools)
- Install system-wide utilities (gh, direnv, podman, tmux, neovim)
- Install modern CLI tools (fzf, zoxide, eza, bat, fd, delta, etc.)
- Install GUI applications (Brave, Slack, Flatpaks)
- Install desktop environment (i3, rofi, fonts)
- Configure system services (sshd, hostname)

**What Box Should NOT Do:**
- Configure shell environment (bashrc, profile)
- Configure user applications (nvim, tmux, git, i3 config)
- Manage symlinks for user configs
- Add configuration to dotfiles-managed files

### Dotfiles Repository
**Purpose:** User configuration and personalization
**Location:** ~/git/personal/dotfiles
**Responsibilities:**
- Shell configuration (bashrc, profile, aliases)
- Editor configuration (nvim/init.lua)
- Git configuration (gitconfig, aliases)
- Window manager configuration (i3 config)
- Terminal multiplexer (tmux.conf)
- Custom scripts (bin/)
- Symlink management

**What Dotfiles Should NOT Do:**
- Install system packages
- Require sudo/root privileges
- Modify system files outside home directory

### Workflow
1. Run Ansible playbook (box) to provision system
2. Manually run dotfiles installation for user configuration
3. Install specific language versions as needed

### Boundary Enforcement
- Ansible installs pyenv/nvm/rbenv but does NOT configure them
- Dotfiles configures pyenv/nvm/rbenv (lazy-loading, shell integration)
- No overlap or duplication between repositories