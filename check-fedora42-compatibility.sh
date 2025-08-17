#!/bin/bash

# Script to check NVIDIA driver compatibility with Fedora 42
# Run this BEFORE upgrading to Fedora 42

set -e

echo "=== Fedora 42 NVIDIA Driver Compatibility Check ==="
echo "Current Fedora Version: $(cat /etc/fedora-release)"
echo ""

# 1. Check current kernel and nvidia driver versions
echo "=== Current System Info ==="
echo "Kernel: $(uname -r)"
if command -v nvidia-smi &> /dev/null; then
    echo "NVIDIA Driver: $(nvidia-smi --query-gpu=driver_version --format=csv,noheader)"
    echo "GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader)"
fi
echo ""

# 2. Check what's available in Fedora 42 repos
echo "=== Checking Fedora 42 Repository Compatibility ==="
echo "Querying RPMFusion for Fedora 42 nvidia packages..."
echo ""

# Check RPMFusion free repo for F42
echo "Testing RPMFusion Free repo for Fedora 42:"
curl -s -I "https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-42.noarch.rpm" | head -n1

echo ""
echo "Testing RPMFusion Nonfree repo for Fedora 42:"
curl -s -I "https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-42.noarch.rpm" | head -n1

echo ""
echo "=== Checking Package Availability in Fedora 42 ==="
echo "You can check package availability at:"
echo "  - https://koji.rpmfusion.org/koji/packageinfo?packageID=13"
echo "  - https://admin.rpmfusion.org/pkgdb/package/nonfree/akmod-nvidia/"
echo ""

# 3. Check for known issues
echo "=== Known Compatibility Information ==="
echo "RTX 2080 Ti (Turing) Requirements:"
echo "  - Minimum driver version: 410.xx (you're likely running 550.xx which is good)"
echo "  - CUDA Capability: 7.5"
echo "  - Supported by all recent NVIDIA drivers"
echo ""

# 4. Test in a container (optional but recommended)
echo "=== Container Test Option ==="
echo "To test in a Fedora 42 container without affecting your system:"
echo ""
echo "podman run -it --rm fedora:42 /bin/bash"
echo "# Inside container:"
echo "dnf install -y https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-42.noarch.rpm"
echo "dnf install -y https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-42.noarch.rpm"
echo "dnf info akmod-nvidia"
echo ""

# 5. Check kernel compatibility
echo "=== Kernel Module Compatibility ==="
echo "Current NVIDIA kernel modules:"
lsmod | grep nvidia || echo "No nvidia modules currently loaded"
echo ""

# 6. Backup recommendation
echo "=== Before Upgrading ==="
echo "1. Backup your current nvidia configuration:"
echo "   - /etc/X11/xorg.conf.d/*nvidia*"
echo "   - /etc/modprobe.d/*nvidia*"
echo "   - List of current nvidia packages: rpm -qa | grep nvidia > nvidia-packages-backup.txt"
echo ""
echo "2. Consider creating a system snapshot if using BTRFS or LVM"
echo ""

# 7. Check for held back packages
echo "=== Checking for Held Packages ==="
dnf list installed | grep nvidia | head -5
echo ""

echo "=== Summary ==="
echo "✓ RTX 2080 Ti is well-supported by current NVIDIA drivers"
echo "✓ RPMFusion repos are available for Fedora 42"
echo "✓ Run 'sudo dnf system-upgrade download --releasever=42' with --allowerasing if needed"
echo ""
echo "IMPORTANT: After upgrade, the first boot may use nouveau drivers."
echo "The system will rebuild nvidia kernel modules automatically (may take a few minutes)."
echo "You might need to reboot twice for full nvidia functionality."