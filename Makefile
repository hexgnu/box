.PHONY: all depends clean check nvidia dev desktop help

# Default target
all: check
	@echo "Running full system configuration..."
	ansible-playbook -K -i hosts jupiter.yml

# Install dependencies
depends:
	sudo dnf install -y ansible make git

# Run with specific tags
nvidia:
	@echo "Installing NVIDIA drivers and CUDA..."
	ansible-playbook -K -i hosts jupiter.yml --tags nvidia

dev:
	@echo "Installing development tools..."
	ansible-playbook -K -i hosts jupiter.yml --tags "development,languages"

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
	@echo "  make all        - Run complete configuration"
	@echo "  make depends    - Install Ansible and dependencies"
	@echo "  make nvidia     - Install NVIDIA drivers only"
	@echo "  make dev        - Install development tools only"
	@echo "  make desktop    - Install desktop applications only"
	@echo "  make containers - Setup Podman only"
	@echo "  make check      - Validate playbook syntax"
	@echo "  make dry-run    - Show what would change without making changes"
	@echo "  make list-tags  - List all available tags"
	@echo "  make clean      - Remove temporary files"
	@echo "  make debug      - Run with verbose output"
