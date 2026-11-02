.PHONY: all update provision fast depends clean check nvidia dev desktop help vim jj cap hermes hermes-mail hermes-sandbox containers

# Default target - quick incremental provisioning (fast, skips if already done)
all: full

# Ultra-fast mode - skips banner and pre/post tasks
fast: check
	@echo "⚡ FAST MODE - No banner, quick tags only"
	ansible-playbook -K -i hosts jupiter.yml --tags quick --skip-tags always --ask-vault-pass

# Quick incremental provisioning (recommended for daily use)
provision: check
	@echo "Running quick incremental provisioning..."
	@echo "This skips already-installed packages and uses state:present"
	ansible-playbook -K -i hosts jupiter.yml --tags quick --ask-vault-pass

# Full system update - upgrade ALL packages to latest versions
update: check
	@echo "⚡ Running FULL SYSTEM UPDATE (dnf upgrade + all managed packages) ⚡"
	@echo "This runs 'dnf upgrade' on the entire system PLUS updates all managed packages"
	@echo "WARNING: This may take 15-20 minutes and will upgrade everything"
	@echo ""
	ansible-playbook -K -i hosts jupiter.yml --tags update --ask-vault-pass

# Complete provisioning without updates (all roles, but state:present)
full: check
	@echo "Running complete provisioning (all roles, incremental mode)..."
	ansible-playbook -K -i hosts jupiter.yml --ask-vault-pass

# Install dependencies
depends:
	sudo dnf install -y ansible make git glibc-devel gcc

# Run with specific tags
nvidia:
	@echo "Installing NVIDIA drivers and CUDA..."
	ansible-playbook -K -i hosts jupiter.yml --tags nvidia --ask-vault-pass

dev:
	@echo "Installing development tools..."
	ansible-playbook -K -i hosts jupiter.yml --tags "development,languages" --ask-vault-pass

vim:
	@echo "INstalling vim"
	ansible-playbook -K -i hosts jupiter.yml --tags "vim" --ask-vault-pass

jj:
	@echo "Installing Jujutsu (jj)..."
	ansible-playbook -K -i hosts jupiter.yml --tags jujutsu --ask-vault-pass

cap:
	@echo "Installing Cap screen recorder..."
	ansible-playbook -K -i hosts jupiter.yml --tags cap --ask-vault-pass

desktop:
	@echo "Installing desktop applications..."
	ansible-playbook -K -i hosts jupiter.yml --tags "desktop,flatpak" --ask-vault-pass

containers:
	@echo "Setting up Podman..."
	ansible-playbook -K -i hosts jupiter.yml --tags podman --ask-vault-pass

hermes:
	@echo "Installing Hermes Agent..."
	ansible-playbook -K -i hosts jupiter.yml --tags hermes --ask-vault-pass

hermes-mail:
	@echo "Refreshing Hermes sandbox mail credentials..."
	ansible-playbook -K -i hosts jupiter.yml --tags hermes-mail --ask-vault-pass

# Rebuilds the sandbox image and removes any container built from an older one.
# ~4 minutes cold (it compiles himalaya and ortie from source); cached layers make
# a no-op rerun fast. Needed after editing hermes/files/sandbox/Dockerfile.
#
# Skill edits do NOT need this: skills are read in place from the dotfiles repo via
# skills.external_dirs, so they are live as soon as the file is saved.
hermes-sandbox:
	@echo "Rebuilding the Hermes sandbox image..."
	ansible-playbook -K -i hosts jupiter.yml --tags hermes-sandbox --ask-vault-pass

# Check syntax
check:
	@echo "Checking playbook syntax..."
	ansible-playbook --syntax-check jupiter.yml

# List all available tags
list-tags:
	ansible-playbook jupiter.yml --list-tags

# Dry run - show what would change
dry-run:
	ansible-playbook -K -i hosts jupiter.yml --check --diff --ask-vault-pass

# Dry run for quick provisioning
dry-run-quick:
	@echo "Checking what would change with quick provisioning..."
	ansible-playbook -K -i hosts jupiter.yml --check --diff --tags quick --ask-vault-pass

# Verbose mode to see what's actually running
verbose:
	@echo "Running with verbose output to see all actions..."
	ansible-playbook -K -i hosts jupiter.yml --tags quick -v --ask-vault-pass

# Clean up temporary files
clean:
	rm -rf /tmp/ansible_cache /tmp/ansible-retry
	find . -name "*.retry" -delete

# Verbose mode for debugging
debug:
	ansible-playbook -K -i hosts jupiter.yml -vvvv --ask-vault-pass

# Help target
help:
	@echo "Available targets:"
	@echo ""
	@echo "Main Commands:"
	@echo "  make            - Quick incremental provisioning (default, ~5min)"
	@echo "  make fast       - ⚡ FASTEST - Skips banner, quick tags only (~2-3min)"
	@echo "  make provision  - Same as 'make' - fast incremental updates"
	@echo "  make update     - ⚡ FULL SYSTEM UPGRADE - dnf upgrade + all packages (~15-20min)"
	@echo "  make full       - Complete provisioning (all roles, but incremental)"
	@echo ""
	@echo "Setup:"
	@echo "  make depends    - Install Ansible and dependencies"
	@echo ""
	@echo "Selective Provisioning:"
	@echo "  make nvidia     - Install NVIDIA drivers only"
	@echo "  make dev        - Install development tools only"
	@echo "  make vim        - Install vim/neovim only"
	@echo "  make jj         - Install Jujutsu (jj) VCS only"
	@echo "  make cap        - Install Cap screen recorder only"
	@echo "  make desktop    - Install desktop applications only"
	@echo "  make containers - Setup Podman only"
	@echo "  make hermes         - Install Hermes Agent only"
	@echo "  make hermes-mail    - Mail credentials + sandbox mounts"
	@echo "  make hermes-sandbox - Rebuild sandbox image, reap stale containers"
	@echo ""
	@echo "Utilities:"
	@echo "  make check      - Validate playbook syntax"
	@echo "  make dry-run    - Show what would change without making changes"
	@echo "  make list-tags  - List all available tags"
	@echo "  make clean      - Remove temporary files"
	@echo "  make debug      - Run with verbose output"
	@echo ""
	@echo "Recommended workflow:"
	@echo "  - First time:     make full"
	@echo "  - Daily updates:  make"
	@echo "  - Fedora upgrade: make update"
