# Modern CLI Tools Installation Verification Guide

This guide helps verify the modern CLI tools installation via Ansible.

## Installation Commands

### Step 1: Run Syntax Check
```bash
cd /home/hexgnu/git/personal/box
ansible-playbook --syntax-check jupiter.yml
```

### Step 2: Run in Check Mode (Dry Run)
```bash
cd /home/hexgnu/git/personal/box
ansible-playbook -K -i hosts jupiter.yml --tags developer-tools --check
```

### Step 3: Install Modern CLI Tools
```bash
cd /home/hexgnu/git/personal/box
ansible-playbook -K -i hosts jupiter.yml --tags developer-tools
```

Alternatively, install only modern CLI tools:
```bash
cd /home/hexgnu/git/personal/box
ansible-playbook -K -i hosts jupiter.yml --tags cli-tools,modern-tools
```

### Step 4: Verify Installation
Check that all tools are available:
```bash
which fzf zoxide eza bat fd delta lazygit btop tldr rg jq yq
```

### Step 5: Test Each Tool
```bash
# Test fzf
fzf --version

# Test zoxide
zoxide --version

# Test eza
eza --version

# Test bat
bat --version

# Test fd-find
fd --version

# Test git-delta
delta --version

# Test lazygit
lazygit --version

# Test btop
btop --version

# Test tldr
tldr --version

# Test ripgrep
rg --version

# Test jq
jq --version

# Test yq
yq --version
```

## Package Availability Status

### Available in Standard Fedora 42 Repos

These packages can be installed directly via `dnf` without additional repositories:

1. **fzf** - Fuzzy finder for interactive searching
2. **zoxide** - Smart cd alternative that learns your habits
3. **bat** - Cat clone with syntax highlighting
4. **fd-find** - Fast and user-friendly alternative to find
5. **btop** - Resource monitor with better UI than htop
6. **ripgrep** - Extremely fast grep alternative
7. **jq** - Command-line JSON processor

### May Require COPR or Alternative Installation

These packages might not be available in standard repos and may need COPR repositories or manual installation:

8. **eza** - Modern ls with colors and git integration
   - Status: NOT in Fedora 42 standard repos (maintainer orphaned package)
   - Install via COPR: `sudo dnf copr enable atim/eza && sudo dnf install eza`
   - Or download from: https://github.com/eza-community/eza/releases/latest
   - Or install via cargo: `cargo install eza`

9. **git-delta** - Syntax-highlighted git diffs with line numbers
   - May require COPR or cargo installation

10. **lazygit** - Terminal UI for git commands
    - Install via COPR: `sudo dnf copr enable atim/lazygit && sudo dnf install lazygit`
    - Alternative: Terra repository or manual download

11. **tldr** - Community-driven simplified man pages
    - May be available as 'tealdeer' package (Rust implementation)
    - Or install via npm: `npm install -g tldr`

12. **yq** - YAML processor (like jq for YAML)
    - Check standard repos first, may need COPR

## Troubleshooting

### If a package is not available in Fedora 42 repos:

Check if the package exists:
```bash
dnf search <package-name>
```

Check package info:
```bash
dnf info <package-name>
```

Check if the package might be in a different repo:
```bash
dnf repolist
dnf --enablerepo=* search <package-name>
```

### Alternative Installation Methods

If some packages are not available via DNF, they may need to be installed via:
- **cargo** (Rust package manager) - for rust-based tools
- **COPR** repositories - community repositories for Fedora
- **Direct binary download** - from GitHub releases

## Files Modified

The following files were updated to add modern CLI tools:

1. `/home/hexgnu/git/personal/box/developer-tools/tasks/main.yml`
   - Added "Install modern CLI tools" task
   - Added verification tasks

2. `/home/hexgnu/git/personal/box/developer-tools/defaults/main.yml`
   - Documented modern CLI tools
   - Updated rust_cargo_packages to remove duplicates

## Success Criteria

- [ ] Ansible syntax check passes
- [ ] Ansible playbook runs without errors
- [ ] All 12 tools are available via `which` command
- [ ] All tools report version when called with `--version`
- [ ] No "WARNING: X is not available in PATH" messages from Ansible verification tasks
