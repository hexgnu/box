.PHONY: all update provision fast depends clean check nvidia dev desktop help vim

# Default target - quick incremental provisioning (fast, skips if already done)
all: provision

# Ultra-fast mode - skips banner and pre/post tasks
fast: check
	@echo "⚡ FAST MODE - No banner, quick tags only"
	ansible-playbook -K -i hosts jupiter.yml --tags quick --skip-tags always

# Quick incremental provisioning (recommended for daily use)
provision: check
	@echo "Running quick incremental provisioning..."
	@echo "This skips already-installed packages and uses state:present"
	ansible-playbook -K -i hosts jupiter.yml --tags quick

# Full system update - upgrade all packages to latest versions
update: check
	@echo "Running full system update (upgrades to latest versions)..."
	@echo "This will update all managed packages to their latest versions"
	ansible-playbook -K -i hosts jupiter.yml --tags update

# Complete provisioning without updates (all roles, but state:present)
full: check
	@echo "Running complete provisioning (all roles, incremental mode)..."
	ansible-playbook -K -i hosts jupiter.yml

# Install dependencies
depends:
	sudo dnf install -y ansible make git glibc-devel gcc

# Run with specific tags
nvidia:
	@echo "Installing NVIDIA drivers and CUDA..."
	ansible-playbook -K -i hosts jupiter.yml --tags nvidia

dev:
	@echo "Installing development tools..."
	ansible-playbook -K -i hosts jupiter.yml --tags "development,languages"

vim:
	@echo "INstalling vim"
	ansible-playbook -K -i hosts jupiter.yml --tags "vim"
desktop:
	@echo "Installing desktop applications..."
	ansible-playbook -K -i hosts jupiter.yml --tags "desktop,flatpak"

containers:
	@echo "Setting up Podman..."
	ansible-playbook -K -i hosts jupiter.yml --tags podman

# Check syntax
check:
	@echo "Checking playbook syntax..."
	ansible-playbook --syntax-check jupiter.yml

# List all available tags
list-tags:
	ansible-playbook jupiter.yml --list-tags

# Dry run - show what would change
dry-run:
	ansible-playbook -K -i hosts jupiter.yml --check --diff

# Clean up temporary files
clean:
	rm -rf /tmp/ansible_cache /tmp/ansible-retry
	find . -name "*.retry" -delete

# Verbose mode for debugging
debug:
	ansible-playbook -K -i hosts jupiter.yml -vvvv

# Help target
help:
	@echo "Available targets:"
	@echo ""
	@echo "Main Commands:"
	@echo "  make            - Quick incremental provisioning (default, ~5min)"
	@echo "  make fast       - ⚡ FASTEST - Skips banner, quick tags only (~2-3min)"
	@echo "  make provision  - Same as 'make' - fast incremental updates"
	@echo "  make update     - Full system upgrade (updates all to latest versions)"
	@echo "  make full       - Complete provisioning (all roles, but incremental)"
	@echo ""
	@echo "Setup:"
	@echo "  make depends    - Install Ansible and dependencies"
	@echo ""
	@echo "Selective Provisioning:"
	@echo "  make nvidia     - Install NVIDIA drivers only"
	@echo "  make dev        - Install development tools only"
	@echo "  make vim        - Install vim/neovim only"
	@echo "  make desktop    - Install desktop applications only"
	@echo "  make containers - Setup Podman only"
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
