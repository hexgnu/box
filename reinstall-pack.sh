#!/usr/bin/env bash

DIR=fedora-home-$(hostname)-$(date +%Y%m%d)
mkdir -p $DIR
cd $DIR

sudo dnf history userinstalled > packages-userinstalled.txt || true
sudo dnf repolist --enabled > repos-enabled.txt
sudo dnf repoquery --extras > packages-extras.txt || true
sudo dnf repoquery --unsatisfied > packages-unsatisfied.txt || true
sudo dnf repoquery --duplicates > packages-duplicates.txt || true

# B. Flatpaks & language toolchains
flatpak remotes -d > flatpak-remotes.txt || true
flatpak list --app --columns=application,origin > flatpak-list.txt || true
pipx list > pipx.txt 2>/dev/null || true
python3 -m pip list --user > pip-user.txt 2>/dev/null || true
command -v cargo >/dev/null && cargo install --list > cargo.txt || true
command -v npm >/dev/null && npm -g list --depth=0 > npm-global.txt || true
command -v go >/dev/null && echo "GOPATH: $(go env GOPATH)" > go.txt || true

# C. Services, timers, cron
systemctl list-unit-files --state=enabled > systemd-enabled.txt
systemctl --user list-unit-files --state=enabled > systemd-user-enabled.txt
systemctl list-timers --all > systemd-timers.txt
crontab -l > crontab.txt 2>/dev/null || true
sudo ls -1 /etc/cron.* > cron-system.txt 2>/dev/null || true

# D. Config drift under /etc
sudo find /etc -type f -name '*.rpmnew' -o -name '*.rpmsave' > etc-rpmnew-rpmsave.txt || true
sudo bash -c "find /etc -type f -not -path '/etc/ssl/*' -print0 | \
  xargs -0 rpm -qf 2>&1 | grep 'is not owned' | \
  sed 's/^file //; s/ is not owned.*//' > etc-unowned.txt"

# E. i3 + dotfiley things
mkdir -p i3
[ -f ~/.config/i3/config ] && cp ~/.config/i3/config i3/
[ -f ~/.config/i3status/config ] && cp ~/.config/i3status/config i3/
[ -f ~/.config/i3blocks/config ] && cp ~/.config/i3blocks/config i3/
[ -f ~/.Xresources ] && cp ~/.Xresources i3/ || true

# F. Desktop/app prefs (catch-all)
command -v dconf >/dev/null && dconf dump / > dconf-dump.ini || true

# G. Network, printers, firewall (optional but nice)
sudo tar czf networkmanager-connections.tgz /etc/NetworkManager/system-connections 2>/dev/null || true
lpstat -p -d > printers.txt 2>/dev/null || true
sudo firewall-cmd --list-all > firewalld.txt 2>/dev/null || true

# H. Containers/VMs (if applicable)
podman ps -a --format '{{.Names}} {{.Image}}' > podman-containers.txt 2>/dev/null || true
podman volume ls > podman-volumes.txt 2>/dev/null || true
virsh list --all > libvirt-vms.txt 2>/dev/null || true

# I. Keys & secrets (handle carefully; store offline!)
mkdir keys
cp -a ~/.ssh keys/ssh 2>/dev/null || true
gpg --export --armor > keys/gpg-public.asc 2>/dev/null || true
gpg --export-secret-keys --armor > keys/gpg-private.asc 2>/dev/null || true
gpg --export-ownertrust > keys/gpg-ownertrust.txt 2>/dev/null || true

echo "DONE -> $(pwd)"
