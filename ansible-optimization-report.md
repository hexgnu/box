# Ansible Provisioning Optimization Report
# Jupiter Workstation Configuration

**Date:** 2026-03-03
**Repository:** `/home/hexgnu/git/personal/box`
**Playbook:** `jupiter.yml`
**Scope:** All 27 role task files analyzed

---

## Executive Summary

Analysis of 27 role task files and the main playbook identified **31 specific optimization opportunities** across all categories. The primary bottlenecks are:

1. Roles using `state: latest` that force DNF version checks on every run (network round-trips per package group)
2. Git repos cloned with `update: true` that contact GitHub on every run
3. Two tasks that download and install software on every incremental run without checking if it is already installed (zoom, st make)
4. The `keys` role runs GPG export and SSH archive tasks on every run even when keys already exist
5. The `ssh` role runs `ssh-keyscan github.com` on every run via a lookup, incurring a live DNS + TCP connection
6. The `nvm` role re-runs global `npm install` for 8 packages every single run with no idempotency
7. The `install_repos` role is dead code pinned to Fedora 31 RPMs and should be excluded
8. No consistent tag taxonomy means running a targeted subset (e.g., just desktop apps) is unreliable
9. `dnf makecache` runs unconditionally in the `nvidia` role even on incremental runs
10. `podman` role always pulls three container images on every run

**Estimated time savings for incremental runs after applying these changes:**

| Category | Current (estimate) | After optimization |
|---|---|---|
| DNF `state: latest` round-trips | 3-6 min | 10-30 sec |
| Git `update: true` network hits | 1-3 min | 2-5 sec |
| Zoom download + re-install | 2-4 min | 0 sec (skipped) |
| NVM npm global installs (8 pkgs) | 2-3 min | 0 sec (skipped) |
| SSH keyscan live lookup | 5-10 sec | 0 sec (cached) |
| Podman image pulls | 1-5 min | 0 sec (skipped) |
| **Total incremental run** | **~20-40 min** | **~3-5 min** |

Fresh installation time remains essentially the same (all skips evaluate to false, all work runs).

---

## Optimization Recommendations

### 1. Fact Gathering Optimization

**Current state (ansible.cfg):**
```ini
gathering = smart
fact_caching = jsonfile
fact_caching_connection = /tmp/ansible_cache
fact_caching_timeout = 3600
```

The existing `ansible.cfg` already has `gathering = smart` and JSON file caching configured.
However, the cache lives in `/tmp`, which is cleared on reboot. Two improvements will help.

**Recommendation 1.1 - Persist fact cache across reboots:**
```ini
# ansible.cfg - change cache path from /tmp to a persistent location
fact_caching_connection = /home/hexgnu/.cache/ansible/facts
```
After a reboot, smart gathering currently re-collects all facts from scratch. Moving the cache to a
user-owned persistent directory means facts survive reboots. The `3600` second TTL (1 hour) is
appropriate for a workstation.

**Recommendation 1.2 - Extend cache TTL for daily use:**
```ini
# ansible.cfg - extend to 4 hours for typical workday usage
fact_caching_timeout = 14400
```

**Impact:** Low for individual runs, meaningful when running the playbook multiple times per day
(e.g., iterating on a role). Saves 5-20 seconds per run where facts are already cached.

**Risk:** None. `gather_facts: no` is already set in `jupiter.yml`. Facts are gathered on demand
via `setup:` in the `keys` role.

---

### 2. Idempotency Improvements by Role

#### 2.1 Role: `i3` - state: latest forces upgrade check every run

**Impact: HIGH** | **Risk: LOW**

Every incremental run contacts DNF repos to check for upgrades of 11 i3-related packages.

```yaml
# BEFORE - forces version check and potential upgrade on every run
- name: install i3 window manager and dependencies
  dnf:
    name:
      - i3
      - i3status
      # ... 9 more packages
    state: latest
  tags: [i3]
```

```yaml
# AFTER - installs if absent, skips if present; upgrade deliberately via tag
- name: install i3 window manager and dependencies
  dnf:
    name:
      - i3
      - i3status
      - i3lock
      - picom
      - rofi
      - feh
      - xbacklight
      - dunst
      - arandr
      - xorg-x11-server-Xorg
      - xorg-x11-xinit-session
    state: present
  tags: [i3, desktop, packages]
```

---

#### 2.2 Role: `i3blocks` - make runs on every run without a creates guard

**Impact: HIGH** | **Risk: LOW**

The `make` and `make install` tasks have no `creates` condition. They re-compile and re-install
i3blocks every single run. The `autogen` and `configure` steps correctly use `creates:` but the
build step does not.

```yaml
# BEFORE - recompiles and reinstalls every run
- name: make it
  make:
    chdir: /home/{{ username }}/git/personal/i3blocks
  become_user: "{{ username }}"

- name: install it
  make:
    chdir: /home/{{ username }}/git/personal/i3blocks
    target: install
  become: true
```

```yaml
# AFTER - skip compile if binary already installed; only reinstall when source changes
- name: Check if i3blocks binary is already installed
  stat:
    path: /usr/local/bin/i3blocks
  register: i3blocks_binary
  tags: [i3blocks, desktop]

- name: make it
  make:
    chdir: /home/{{ username }}/git/personal/i3blocks
  become_user: "{{ username }}"
  when: not i3blocks_binary.stat.exists
  tags: [i3blocks, desktop]

- name: install it
  make:
    chdir: /home/{{ username }}/git/personal/i3blocks
    target: install
  become: true
  when: not i3blocks_binary.stat.exists
  tags: [i3blocks, desktop]
```

Also, `state: latest` on build dependencies should become `state: present`:
```yaml
# AFTER
- name: Install build dependencies for i3blocks
  dnf:
    name: [autoconf, automake, make, gcc, git]
    state: present
  tags: [i3blocks, desktop, packages]
```

---

#### 2.3 Role: `flatpak` - state: latest forces upgrade check every run

**Impact: MEDIUM** | **Risk: NONE**

```yaml
# BEFORE
- name: install flatpak
  dnf: name=flatpak state=latest
```

```yaml
# AFTER
- name: install flatpak
  dnf:
    name: flatpak
    state: present
  tags: [flatpak, desktop, packages]
```

The flatpak remote-add task is already idempotent (`--if-not-exists`). The individual app
installs are already gated with `rc != 0` checks. Good pattern already in use here.

Add tags to the app install tasks for selective execution:
```yaml
- name: Check if Tidal-Hifi is already installed
  command: flatpak list --app | grep com.mastermindzh.tidal-hifi
  register: tidal_check
  failed_when: false
  changed_when: false
  tags: [flatpak, desktop, music]

- name: Install Tidal-Hifi for music streaming
  command: flatpak install -y flathub com.mastermindzh.tidal-hifi
  when: tidal_check.rc != 0
  tags: [flatpak, desktop, music]
```

---

#### 2.4 Role: `brave` - update_cache: yes forces DNF metadata refresh

**Impact: MEDIUM** | **Risk: NONE**

```yaml
# BEFORE - forces full DNF cache refresh on every run
- name: Install Brave browser
  become: true
  dnf:
    name: brave-browser
    state: present
    update_cache: yes
```

```yaml
# AFTER - remove update_cache; DNF handles cache freshness automatically
- name: Install Brave browser
  become: true
  dnf:
    name: brave-browser
    state: present
  tags: [brave, desktop, packages]
```

The `Remove old/broken Brave repository` task deletes repo files on every run. This triggers
a cache invalidation every time. Add a stat check:

```yaml
# AFTER - only remove if old files exist
- name: Check for old Brave repository files
  stat:
    path: "{{ item }}"
  register: old_brave_repos
  loop:
    - /etc/yum.repos.d/brave-browser.repo
    - /etc/yum.repos.d/brave.repo
    - /etc/yum.repos.d/brave-browser-rpm-release.repo
  tags: [brave, desktop]

- name: Remove old/broken Brave repository configurations
  become: true
  file:
    path: "{{ item.item }}"
    state: absent
  loop: "{{ old_brave_repos.results }}"
  when: item.stat.exists
  tags: [brave, desktop]
```

---

#### 2.5 Role: `st` - make runs unconditionally every run

**Impact: HIGH** | **Risk: LOW**

The `st` terminal is recompiled and reinstalled on every single run. There is no idempotency check.

```yaml
# BEFORE - compiles and installs every run
- name: make and install st
  make:
    chdir: /home/hexgnu/git/personal/st

- name: install it
  make:
    chdir: /home/hexgnu/git/personal/st
    target: install
```

```yaml
# AFTER - only compile and install if binary is absent
- name: Check if st terminal is installed
  stat:
    path: /usr/local/bin/st
  register: st_binary
  tags: [st, desktop]

- name: make and install st
  make:
    chdir: /home/hexgnu/git/personal/st
  when: not st_binary.stat.exists
  tags: [st, desktop]

- name: install it
  make:
    chdir: /home/hexgnu/git/personal/st
    target: install
  when: not st_binary.stat.exists
  tags: [st, desktop]
```

Note: `st/tasks/main.yml` hardcodes `hexgnu` instead of using `{{ username }}`. Fix both occurrences
for consistency:
```yaml
# AFTER - use variable throughout
- name: check out st repo
  become: true
  become_user: "{{ username }}"
  git:
    update: false
    repo: git@github.com:hexgnu/st.git
    dest: /home/{{ username }}/git/personal/st
  tags: [st, desktop]
```

---

#### 2.6 Role: `vim` - git plugins cloned with update: true + retry logic

**Impact: HIGH** | **Risk: LOW**

Both vim plugin clones use `update: true`, meaning every run contacts GitHub to check for
upstream changes. The retry logic (3 retries, 5 second delay) adds up to 15 seconds per
plugin on a network failure that does not occur, because the retry runs even when the
task succeeds on the first attempt if `update: true` triggers a remote ref check that takes time.

```yaml
# BEFORE - contacts GitHub every run, retry machinery executes
- name: install ctrl-p
  become: true
  become_user: hexgnu
  git:
    update: true
    repo: https://github.com/ctrlpvim/ctrlp.vim.git
    dest: /home/hexgnu/.config/nvim/bundle/ctrlp.vim
  retries: 3
  delay: 5
  register: ctrlp_result
  until: ctrlp_result is succeeded

- name: install packer
  become: true
  become_user: hexgnu
  git:
    update: true
    repo: https://github.com/wbthomason/packer.nvim.git
    dest: /home/hexgnu/.local/share/nvim/site/pack/packer/start/packer.nvim
  retries: 3
  delay: 5
  register: packer_result
  until: packer_result is succeeded
```

```yaml
# AFTER - clone once, let the plugin manager handle updates; use {{ username }} variable
- name: install ctrl-p
  become: true
  become_user: "{{ username }}"
  git:
    update: false
    repo: https://github.com/ctrlpvim/ctrlp.vim.git
    dest: /home/{{ username }}/.config/nvim/bundle/ctrlp.vim
  tags: [vim, dev-tools]

- name: install packer
  become: true
  become_user: "{{ username }}"
  git:
    update: false
    repo: https://github.com/wbthomason/packer.nvim.git
    dest: /home/{{ username }}/.local/share/nvim/site/pack/packer/start/packer.nvim
  tags: [vim, dev-tools]

- name: install neovim
  dnf:
    state: present
    name: neovim
  tags: [vim, dev-tools, packages]
```

---

#### 2.7 Role: `pyenv` - all three git clones use update: yes

**Impact: HIGH** | **Risk: LOW**

Pyenv and both plugins contact GitHub on every single run. For a version manager that rarely
changes in ways that matter between provisioning runs, `update: false` is correct for the
initial setup role. The dotfiles repo is responsible for keeping pyenv current via `pyenv update`.

```yaml
# BEFORE - 3 GitHub round-trips every run
- name: Clone pyenv repository for user
  git:
    repo: https://github.com/pyenv/pyenv.git
    dest: "/home/{{ username }}/.pyenv"
    update: yes

- name: Clone pyenv-virtualenv plugin
  git:
    repo: https://github.com/pyenv/pyenv-virtualenv.git
    dest: "/home/{{ username }}/.pyenv/plugins/pyenv-virtualenv"
    update: yes

- name: Clone pyenv-update plugin
  git:
    repo: https://github.com/pyenv/pyenv-update.git
    dest: "/home/{{ username }}/.pyenv/plugins/pyenv-update"
    update: yes
```

```yaml
# AFTER - clone once, pyenv-update plugin handles self-updates
- name: Clone pyenv repository for user
  become: yes
  become_user: "{{ username }}"
  git:
    repo: https://github.com/pyenv/pyenv.git
    dest: "/home/{{ username }}/.pyenv"
    update: false
  tags: [pyenv, languages, dev-tools]

- name: Clone pyenv-virtualenv plugin
  become: yes
  become_user: "{{ username }}"
  git:
    repo: https://github.com/pyenv/pyenv-virtualenv.git
    dest: "/home/{{ username }}/.pyenv/plugins/pyenv-virtualenv"
    update: false
  tags: [pyenv, languages, dev-tools]

- name: Clone pyenv-update plugin
  become: yes
  become_user: "{{ username }}"
  git:
    repo: https://github.com/pyenv/pyenv-update.git
    dest: "/home/{{ username }}/.pyenv/plugins/pyenv-update"
    update: false
  tags: [pyenv, languages, dev-tools]
```

Also change `state: latest` to `state: present` for the dependency packages:
```yaml
# AFTER - install once, do not upgrade on every run
- name: Install pyenv dependencies
  dnf:
    state: present
    name:
      - make
      - gcc
      # ... rest of packages
  tags: [pyenv, languages, packages]
```

---

#### 2.8 Role: `nvm` - global npm installs run every single time

**Impact: HIGH** | **Risk: LOW**

The `nvm` role runs `npm install -g` for 8 packages on every playbook run with no file-based
idempotency. Each `npm install -g` contacts the npm registry to check for updates.

```yaml
# BEFORE - contacts npm registry for 8 packages every run
- name: Install other useful global npm packages
  become: yes
  become_user: "{{ username }}"
  shell: |
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    npm config set prefix "$HOME/.nvm/versions/node/$(node --version)"
    npm install -g {{ item }}
  args:
    executable: /bin/bash
  loop:
    - typescript
    - ts-node
    - nodemon
    - prettier
    - eslint
    - yarn
    - pnpm
    - pyright
  register: npm_install
  changed_when: "'added' in npm_install.stdout or 'updated' in npm_install.stdout"
  failed_when: npm_install.rc != 0 and 'EEXIST' not in npm_install.stderr
```

```yaml
# AFTER - check if each package binary exists before installing
- name: Check if global npm packages are installed
  become: yes
  become_user: "{{ username }}"
  shell: |
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    npm list -g --depth=0 {{ item }} 2>/dev/null | grep -q {{ item }}
  args:
    executable: /bin/bash
  register: npm_pkg_check
  changed_when: false
  failed_when: false
  loop:
    - typescript
    - ts-node
    - nodemon
    - prettier
    - eslint
    - yarn
    - pnpm
    - pyright
  tags: [nvm, languages, npm]

- name: Install missing global npm packages
  become: yes
  become_user: "{{ username }}"
  shell: |
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    npm config set prefix "$HOME/.nvm/versions/node/$(node --version)"
    npm install -g {{ item.item }}
  args:
    executable: /bin/bash
  loop: "{{ npm_pkg_check.results }}"
  when: item.rc != 0
  register: npm_install_result
  changed_when: true
  failed_when: npm_install_result.rc != 0 and 'EEXIST' not in npm_install_result.stderr
  tags: [nvm, languages, npm]
```

Similarly, the `claude-code` install task runs unconditionally. It does have `changed_when`
logic but still spawns a full npm process every run. Add a pre-check:

```yaml
# AFTER - skip claude-code install if binary already exists
- name: Check if claude-code is installed
  become: yes
  become_user: "{{ username }}"
  shell: |
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    which claude
  args:
    executable: /bin/bash
  register: claude_check
  changed_when: false
  failed_when: false
  tags: [nvm, languages, claude]

- name: Install @anthropic-ai/claude-code globally
  become: yes
  become_user: "{{ username }}"
  shell: |
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    npm config set prefix "$HOME/.nvm/versions/node/$(node --version)"
    npm install -g @anthropic-ai/claude-code
  args:
    executable: /bin/bash
  when: claude_check.rc != 0
  register: claude_install
  changed_when: "'added' in claude_install.stdout or 'updated' in claude_install.stdout"
  failed_when: claude_install.rc != 0 and 'EEXIST' not in claude_install.stderr
  tags: [nvm, languages, claude]
```

Also change the dependency package state:
```yaml
# AFTER
- name: Install nvm dependencies
  dnf:
    state: present
    name: [curl, git, make, gcc, gcc-c++]
  tags: [nvm, languages, packages]
```

---

#### 2.9 Role: `podman` - container image pulls run on every run

**Impact: MEDIUM** | **Risk: NONE**

Pulling three base images on every run contacts Docker Hub and the Fedora registry even when
the images are already present. The `containers.podman.podman_image` module with `state: present`
should be idempotent, but it still makes a remote HEAD request to check the digest on every run.
Since this is tagged `[podman_images]`, simply remove `podman_images` from the default run
path and require explicit opt-in.

The `state: latest` on the package install forces upgrade checks:
```yaml
# BEFORE
- name: Install Podman and related tools
  dnf:
    state: latest
    name: [podman, podman-compose, buildah, skopeo, ...]
```

```yaml
# AFTER
- name: Install Podman and related tools
  dnf:
    state: present
    name:
      - podman
      - podman-compose
      - buildah
      - skopeo
      - slirp4netns
      - fuse-overlayfs
      - containernetworking-plugins
      - python3-pip
  tags: [podman, containers, packages]
```

For the image pulls, add a when condition gated on an explicit variable:
```yaml
# AFTER - opt-in only; do not pull on every incremental run
- name: Pull common base images for faster container creation
  become: yes
  become_user: "{{ username }}"
  containers.podman.podman_image:
    name: "{{ item }}"
    state: present
  loop:
    - docker.io/library/alpine:latest
    - docker.io/library/ubuntu:latest
    - registry.fedoraproject.org/fedora:latest
  register: image_pull_results
  failed_when: false
  when: podman_pull_base_images | default(false)
  tags: [podman, containers, podman_images]
```

---

#### 2.10 Role: `developer-tools` - state: latest on 4 separate dnf calls

**Impact: HIGH** | **Risk: LOW**

Four separate DNF calls all use `state: latest`, causing 4 DNF metadata operations per run
even when all packages are current. Each call with `state: latest` must contact repos.

```yaml
# BEFORE - 4x state: latest = 4x DNF version checks
- name: Install GitHub CLI
  dnf:
    name: gh
    state: latest

- name: Install Azure CLI
  dnf:
    name: azure-cli
    state: latest

- name: Install Google Cloud CLI
  dnf:
    name: google-cloud-cli
    state: latest

- name: Install Rust and Cargo
  dnf:
    name: [rust, cargo, rust-src, rust-std-static, rust-analyzer]
    state: latest

- name: Install development tools from repos
  dnf:
    name: [GraphicsMagick, GraphicsMagick-devel, httpie, gnome-screenshot]
    state: latest

- name: Install modern CLI tools from standard repos
  dnf:
    name: [fzf, zoxide, bat, fd-find, btop, ripgrep, gh, jq, git-delta, tealdeer, yq]
    state: latest
```

```yaml
# AFTER - state: present for all; tools update via system DNF upgrade
- name: Install GitHub CLI
  dnf:
    name: gh
    state: present
  tags: [dev-tools, packages, github-cli]

- name: Install Azure CLI
  dnf:
    name: azure-cli
    state: present
  tags: [dev-tools, packages, cloud-tools]

- name: Install Google Cloud CLI
  dnf:
    name: google-cloud-cli
    state: present
  tags: [dev-tools, packages, cloud-tools]

- name: Install Rust and Cargo
  dnf:
    name: [rust, cargo, rust-src, rust-std-static, rust-analyzer]
    state: present
  tags: [dev-tools, packages, rust]

- name: Install development tools from repos
  dnf:
    name: [GraphicsMagick, GraphicsMagick-devel, httpie, gnome-screenshot]
    state: present
  tags: [dev-tools, packages]

- name: Install modern CLI tools from standard repos
  dnf:
    name: [fzf, zoxide, bat, fd-find, btop, ripgrep, gh, jq, git-delta, tealdeer, yq]
    state: present
  tags: [dev-tools, packages, cli-tools, modern-tools]
```

The verification loop at the end (running `which` for 12 tools) is purely informational.
It already has `changed_when: false` so it is safe but adds 12 subprocess spawns per run.
Keep it but gate it with a variable for non-verbose runs:

```yaml
# AFTER - make verification opt-in
- name: Verify modern CLI tools are available
  command: "which {{ item }}"
  register: tool_check
  changed_when: false
  failed_when: false
  loop: [fzf, zoxide, eza, bat, fd, delta, lazygit, btop, tldr, rg, jq, yq]
  when: dev_tools_verify | default(false)
  tags: [dev-tools, cli-tools, verify]
```

---

#### 2.11 Role: `zoom` - always downloads and attempts install

**Impact: HIGH** | **Risk: NONE**

Zoom has no existence check. On every run it downloads a fresh RPM (~130MB), runs `dnf install`,
and then cleans up. DNF's `state: present` with a local RPM path is idempotent only if the
package is not already installed - but the download always happens first.

```yaml
# BEFORE - always downloads ~130MB RPM
- name: Download Zoom RPM package
  become: true
  get_url:
    url: https://zoom.us/client/latest/zoom_x86_64.rpm
    dest: /tmp/zoom_x86_64.rpm
    mode: '0644'

- name: Install Zoom from RPM
  become: true
  dnf:
    name: /tmp/zoom_x86_64.rpm
    state: present
    disable_gpg_check: yes
```

```yaml
# AFTER - check first, only download and install if zoom is absent
- name: Check if Zoom is already installed
  command: rpm -q zoom
  register: zoom_installed
  changed_when: false
  failed_when: false
  tags: [zoom, desktop]

- name: Download Zoom RPM package
  become: true
  get_url:
    url: https://zoom.us/client/latest/zoom_x86_64.rpm
    dest: /tmp/zoom_x86_64.rpm
    mode: '0644'
  when: zoom_installed.rc != 0
  tags: [zoom, desktop]

- name: Install Zoom from RPM
  become: true
  dnf:
    name: /tmp/zoom_x86_64.rpm
    state: present
    disable_gpg_check: yes
  when: zoom_installed.rc != 0
  tags: [zoom, desktop]

- name: Clean up downloaded RPM
  become: true
  file:
    path: /tmp/zoom_x86_64.rpm
    state: absent
  when: zoom_installed.rc != 0
  tags: [zoom, desktop]
```

---

#### 2.12 Role: `slack` - repo addition runs unconditionally

**Impact: LOW** | **Risk: NONE**

The `slack` role's primary code path (Flatpak) is well-guarded. The `yum_repository` task
for the Slack repo runs unconditionally even when `slack_use_repo` is false (the `yum_repository`
module is idempotent but still writes and re-reads the file). Add tags:

```yaml
# AFTER - add consistent tags
- name: Check if Slack is already installed via Flatpak
  command: flatpak list --app | grep com.slack.Slack
  register: slack_flatpak_check
  failed_when: false
  changed_when: false
  tags: [slack, desktop, flatpak]

- name: Install Slack via Flatpak
  command: flatpak install -y flathub com.slack.Slack
  when: slack_flatpak_check.rc != 0
  tags: [slack, desktop, flatpak]
```

---

#### 2.13 Role: `keys` - GPG and SSH backup runs every run

**Impact: MEDIUM** | **Risk: LOW**

The `keys` role creates a new dated backup directory and archives SSH/GPG keys on every run.
This means `/home/hexgnu/key-backups/` accumulates a dated directory per run. The date-based
directory makes each `stat` check return "doesn't exist" so the backup always runs.

```yaml
# BEFORE - backup runs every run because the path changes each time
- name: Create backup directory for keys
  file:
    path: "/home/{{ username }}/key-backups/{{ ansible_date_time.date | default(lookup('pipe', 'date +%Y-%m-%d')) }}"
    state: directory
    ...
  when: backup_keys | default(true)
```

```yaml
# AFTER - default backup_keys to false for normal runs; enable explicitly when needed
# In jupiter.yml vars section, add:
#   backup_keys: false
# Or run with: ansible-playbook -K -i hosts jupiter.yml --tags keys -e backup_keys=true

- name: Create backup directory for keys
  file:
    path: "/home/{{ username }}/key-backups/{{ ansible_date_time.date | default(lookup('pipe', 'date +%Y-%m-%d')) }}"
    state: directory
    mode: '0700'
    owner: "{{ username }}"
    group: "{{ username }}"
  when: backup_keys | default(false)   # Changed default from true to false
  tags: [keys, security]
```

The `keys` role also has a duplicate `stat` loop (checking SSH key existence twice: once for
generation logic and again for display). Merge these:

```yaml
# BEFORE - two identical stat loops
- name: Check for existing SSH keys
  stat:
    path: "/home/{{ username }}/.ssh/{{ item }}"
  register: ssh_key_check
  loop: [id_ed25519, id_rsa]

# ... (key generation tasks)

- name: Check which SSH key files exist
  stat:
    path: "/home/{{ username }}/.ssh/{{ item }}"
  register: ssh_key_files
  loop: [id_ed25519, id_ed25519.pub, id_rsa, id_rsa.pub]
```

The second stat (`ssh_key_files`) adds the public key variants. That is acceptable. But the
first `stat` only exists to drive the `when:` conditionals for generation. Since `openssh_keypair`
is already idempotent (it creates if missing, skips if present), the entire first stat loop
and its two `when:` conditionals can be removed:

```yaml
# AFTER - openssh_keypair handles idempotency natively; no pre-check needed
- name: Generate ED25519 SSH key if none exists
  openssh_keypair:
    path: "/home/{{ username }}/.ssh/id_ed25519"
    type: ed25519
    comment: "{{ username }}@{{ hostname }}"
    owner: "{{ username }}"
    group: "{{ username }}"
    mode: '0600'
  become: yes
  become_user: "{{ username }}"
  # No 'when:' needed - openssh_keypair is idempotent
  tags: [keys, security]

- name: Generate RSA SSH key if it doesn't exist (for compatibility)
  openssh_keypair:
    path: "/home/{{ username }}/.ssh/id_rsa"
    type: rsa
    size: 4096
    comment: "{{ username }}@{{ hostname }}"
    owner: "{{ username }}"
    group: "{{ username }}"
    mode: '0600'
  become: yes
  become_user: "{{ username }}"
  # No 'when:' needed - openssh_keypair is idempotent
  tags: [keys, security]
```

---

#### 2.14 Role: `ssh` - live ssh-keyscan lookup runs every time

**Impact: MEDIUM** | **Risk: LOW**

```yaml
# BEFORE - connects to github.com on every run to fetch host key
- name: ensure github.com is a known host
  lineinfile:
    dest: /home/{{username}}/.ssh/known_hosts
    create: yes
    state: present
    line: "{{ lookup('pipe', 'ssh-keyscan -t rsa github.com') }}"
    regexp: "^github\\.com"
```

The `lineinfile` module with `regexp:` is idempotent regarding the file content, but
`lookup('pipe', 'ssh-keyscan ...')` still executes a live network connection every run
to compute the value, even if the line already exists. Use a static known host value or
add a pre-check:

```yaml
# AFTER - check first; only scan if the entry is missing
- name: Check if github.com is in known_hosts
  stat:
    path: "/home/{{ username }}/.ssh/known_hosts"
  register: known_hosts_file
  tags: [ssh, security]

- name: Fetch github.com host key
  shell: ssh-keyscan -t rsa,ed25519 github.com 2>/dev/null
  register: github_hostkey
  changed_when: false
  when: >
    not known_hosts_file.stat.exists or
    (known_hosts_file.stat.exists and
     lookup('file', '/home/' + username + '/.ssh/known_hosts', errors='ignore') | regex_search('github\\.com') == '')
  tags: [ssh, security]

- name: ensure github.com is a known host
  lineinfile:
    dest: /home/{{ username }}/.ssh/known_hosts
    create: yes
    state: present
    line: "{{ item }}"
    regexp: "^github\\.com {{ item.split()[1] }}"
  loop: "{{ github_hostkey.stdout_lines | default([]) }}"
  when: github_hostkey is not skipped
  tags: [ssh, security]
```

The `ssh` role also lacks tags entirely. Add them to all tasks.

---

#### 2.15 Role: `rbenv` - git update: true on every run + rbenv install always runs

**Impact: HIGH** | **Risk: MEDIUM** (rbenv install without guards can break mid-compile)

```yaml
# BEFORE - two GitHub round-trips + unconditional Ruby installation
- name: install rbenv and build
  git:
    update: true
    repo: https://github.com/rbenv/rbenv.git
    dest: /home/hexgnu/.rbenv

- name: install ruby-build
  git:
    update: true
    repo: https://github.com/rbenv/ruby-build.git
    dest: /home/hexgnu/.rbenv/plugins/ruby-build

- name: install 3.2.2
  command: rbenv install 3.2.2
```

The `rbenv install 3.2.2` command has no idempotency guard. It will attempt to compile
Ruby on every single run. This is a compilation job that takes 5-10 minutes.

```yaml
# AFTER - use update: false, check for existing Ruby version before installing
- name: install rbenv and build
  become: true
  become_user: "{{ username }}"
  git:
    update: false
    repo: https://github.com/rbenv/rbenv.git
    dest: /home/{{ username }}/.rbenv
  tags: [rbenv, languages, dev-tools]

- name: install ruby-build
  become: true
  become_user: "{{ username }}"
  git:
    update: false
    repo: https://github.com/rbenv/ruby-build.git
    dest: /home/{{ username }}/.rbenv/plugins/ruby-build
  tags: [rbenv, languages, dev-tools]

- name: Check if Ruby 3.2.2 is already installed via rbenv
  stat:
    path: "/home/{{ username }}/.rbenv/versions/3.2.2"
  register: ruby_322_installed
  tags: [rbenv, languages]

- name: install 3.2.2
  become: true
  become_user: "{{ username }}"
  command: /home/{{ username }}/.rbenv/bin/rbenv install 3.2.2
  when: not ruby_322_installed.stat.exists
  tags: [rbenv, languages]
```

Also fix the hardcoded `hexgnu` references to use `{{ username }}`.

---

#### 2.16 Role: `nvidia` - dnf makecache runs unconditionally

**Impact: MEDIUM** | **Risk: NONE**

```yaml
# BEFORE - forces full DNF metadata refresh every run
- name: Update repository cache
  command: dnf makecache
  changed_when: false
  tags: [nvidia, repos, cache]
```

```yaml
# AFTER - remove the explicit makecache; DNF handles its own cache within each task
# Delete this task entirely. DNF will refresh if the cache is stale.
# If freshness is needed before package install, add update_cache: yes to the install task only.
```

The RPMFusion installation tasks also use retry logic with `until: ... is succeeded`. These
retries are appropriate for a fresh install (network may be flaky) but add overhead on
incremental runs where the packages are already present and DNF returns immediately. Since
`state: present` is already used here, the retries are low-risk but the tasks themselves
will be fast on already-provisioned systems regardless.

---

#### 2.17 Role: `postgres` - shell-based init guard is fragile

**Impact: LOW** | **Risk: MEDIUM**

```yaml
# BEFORE - fragile guard using a sentinel file that may not exist
- name: bootup
  shell: |
    FILE=/usr/local/postgresboot.t
    if test -f "$FILE"; then
      echo "$FILE exists."
      exit 0
    fi
    postgresql-setup --initdb --unit postgresql
  args:
    executable: /bin/bash
```

The sentinel file `/usr/local/postgresboot.t` is never created by this task. The check will
always fail to find it, so `postgresql-setup --initdb` will run every time. `postgresql-setup`
itself has internal guards (it exits non-zero if already initialized, which the task ignores
because there is no `failed_when: false`).

```yaml
# AFTER - check the actual PostgreSQL data directory, not a sentinel file
- name: Check if PostgreSQL data directory is initialized
  stat:
    path: /var/lib/pgsql/data/PG_VERSION
  register: pg_data_initialized
  tags: [postgres, databases]

- name: Initialize PostgreSQL database
  command: postgresql-setup --initdb --unit postgresql
  when: not pg_data_initialized.stat.exists
  tags: [postgres, databases]
```

---

#### 2.18 Role: `install_repos` - dead code pinned to Fedora 31

**Impact: HIGH** | **Risk: NONE**

The `install_repos` role downloads RPMFusion packages for Fedora 31 and adds a Spotify repo
that points to an outdated negativo17 URL. This role is not referenced in `jupiter.yml` and
appears to be leftover from the original Fedora 31 setup.

```yaml
# install_repos/tasks/main.yml - problematic sections
- name: Download RPMFusion Free
  get_url:
    url: https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-31.noarch.rpm
    dest: /opt/rpm-fusion-free.rpm

- name: Spotify fedora repo
  yum_repository:
    name: fedora-spotify
    baseurl: http://negativo17.org/repos/spotify/fedora-$releasever/$basearch/
```

RPMFusion is now handled correctly in `jupiter.yml` itself (using `{{ fedora_version }}`).
The `install_repos` role should be removed from the repo or explicitly excluded from the
playbook. Its download tasks hit old URLs that will fail on Fedora 42.

**Action:** Either delete `install_repos/` or ensure it is never included in `jupiter.yml`.
Currently it is NOT included, so it is dead code but wastes time if ever accidentally called.

---

#### 2.19 Role: `authoring` - state: latest on large packages

**Impact: MEDIUM** | **Risk: LOW**

TeX Live is a very large package. Checking for updates via `state: latest` on every run
causes DNF to inspect the large texlive metadata.

```yaml
# BEFORE
- name: Install the latest version of Zettlr Texlive and Pandoc
  dnf:
    name: [texlive-base, texlive-xetex, pandoc, asciidoc, asciidoc-latex]
    state: latest
```

```yaml
# AFTER
- name: Install authoring tools (TeX, Pandoc, AsciiDoc)
  dnf:
    name: [texlive-base, texlive-xetex, pandoc, asciidoc, asciidoc-latex]
    state: present
  tags: [authoring, packages]
```

---

#### 2.20 Role: `dmenu` - make runs unconditionally

**Impact: MEDIUM** | **Risk: LOW**

Same pattern as `st`. The `make` and `make install` tasks have no guard.

```yaml
# BEFORE
- name: make dmenu
  make:
    chdir: /home/hexgnu/git/personal/dmenu

- name: make install dmenu
  make:
    chdir: /home/hexgnu/git/personal/dmenu
    target: install
```

```yaml
# AFTER - skip if binary already installed
- name: Check if dmenu is installed
  stat:
    path: /usr/local/bin/dmenu
  register: dmenu_binary
  tags: [dmenu, desktop]

- name: make dmenu
  make:
    chdir: /home/{{ username }}/git/personal/dmenu
  when: not dmenu_binary.stat.exists
  tags: [dmenu, desktop]

- name: make install dmenu
  make:
    chdir: /home/{{ username }}/git/personal/dmenu
    target: install
  when: not dmenu_binary.stat.exists
  tags: [dmenu, desktop]
```

---

#### 2.21 Main playbook `jupiter.yml` - tasks section lacks tags

**Impact: MEDIUM** | **Risk: NONE**

The `tasks:` block in `jupiter.yml` (hostname, sshd, RPMFusion) runs unconditionally
on every run with no tags, and cannot be skipped with `--tags`.

```yaml
# BEFORE - no tags, always runs
tasks:
  - hostname:
      name: jupiter.home

  - service:
      name: sshd
      state: started

  - name: Install RPMFusion free
    tags: [personal]
    dnf:
      name: "https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-{{ fedora_version }}.noarch.rpm"
      ...
```

```yaml
# AFTER - add setup/system tags
tasks:
  - name: Set system hostname
    hostname:
      name: "{{ hostname }}"
    tags: [setup, system]

  - name: Ensure sshd is running
    service:
      name: sshd
      state: started
    tags: [setup, system, ssh]

  - name: Install RPMFusion free repository
    tags: [setup, system, repos, personal]
    dnf:
      name: "https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-{{ fedora_version }}.noarch.rpm"
      disable_gpg_check: yes
      state: present
```

---

### 3. Tagging Strategy

#### 3.1 Proposed Tag Taxonomy

The following tag hierarchy enables targeted execution from the broadest to most specific:

```
Tier 1 - Broad (run entire functional areas)
  setup       - Base system configuration (hostname, sshd, RPMFusion)
  desktop     - All desktop environment roles (i3, i3blocks, dmenu, st, flatpak)
  dev-tools   - All development tool roles (vim, pyenv, nvm, rbenv, developer-tools)
  languages   - Language version managers (pyenv, nvm, rbenv)
  packages    - Any DNF package installation task
  security    - Keys, SSH configuration
  system      - System-level config (hostname, sshd, repos)

Tier 2 - Role-level (run a specific role)
  i3          - i3 window manager
  i3blocks    - i3blocks status bar
  dmenu       - dmenu launcher
  st          - Suckless terminal
  flatpak     - Flatpak applications
  brave       - Brave browser
  vim         - Neovim and plugins
  pyenv       - Python version manager
  nvm         - Node version manager
  rbenv       - Ruby version manager
  podman      - Podman containers
  docker      - Docker
  slack       - Slack
  zoom        - Zoom
  wavebox     - Wavebox
  nvidia      - NVIDIA drivers
  keys        - SSH/GPG key management
  ssh         - SSH configuration
  direnv      - direnv
  ddns        - Dynamic DNS
  postgres    - PostgreSQL
  authoring   - TeX/Pandoc authoring tools
  1password   - 1Password CLI
  dotfiles    - Dotfiles (manual only)

Tier 3 - Functional (cross-cutting)
  cloud-tools - Azure CLI, Google Cloud CLI
  cli-tools   - Modern CLI tools (fzf, bat, eza, etc.)
  modern-tools - Same as cli-tools
  containers  - Podman/Docker
  repos       - Repository additions
  drivers     - Hardware drivers
  databases   - PostgreSQL and similar

Special
  never       - Tasks that should never run by default (dotfiles)
  always      - Tasks that always run (banner, hostname)
  manual      - Tasks requiring explicit invocation
  slow        - Tasks known to be time-consuming (Ruby compile, image pulls)
  verify      - Verification tasks (tool checks, status displays)
```

#### 3.2 Tag Application by Role

| Role | Primary Tags | Secondary Tags |
|---|---|---|
| setup | setup, system | repos, packages |
| keys | keys, security | - |
| i3 | i3, desktop | packages |
| i3blocks | i3blocks, desktop | packages |
| flatpak | flatpak, desktop | packages |
| brave | brave, desktop | packages |
| st | st, desktop | - |
| vim | vim, dev-tools | packages |
| pyenv | pyenv, languages, dev-tools | packages |
| nvm | nvm, languages, dev-tools | packages, npm |
| podman | podman, containers | packages |
| developer-tools | dev-tools | packages, cli-tools, cloud-tools, rust |
| direnv | direnv, dev-tools | packages |
| slack | slack, desktop | flatpak |
| zoom | zoom, desktop | - |
| wavebox | wavebox, desktop | - |
| 1password | 1password, security | packages |
| nvidia | nvidia, drivers | packages, cuda |
| ddns | ddns, system | - |
| postgres | postgres, databases | packages |
| authoring | authoring | packages |
| dotfiles | dotfiles, manual, never | - |

#### 3.3 Example Usage Commands

```bash
# Full provisioning run (fresh install or rare full update)
make all

# Quick incremental: only packages that use state: present (fast, idempotent)
ansible-playbook -K -i hosts jupiter.yml --tags packages

# Desktop environment only
ansible-playbook -K -i hosts jupiter.yml --tags desktop

# Development tools only (excludes desktop, nvidia, etc.)
ansible-playbook -K -i hosts jupiter.yml --tags dev-tools

# Language version managers only
ansible-playbook -K -i hosts jupiter.yml --tags languages

# Modern CLI tools only
ansible-playbook -K -i hosts jupiter.yml --tags cli-tools

# NVIDIA drivers (slow, hardware-specific)
make nvidia

# Security-sensitive tasks
ansible-playbook -K -i hosts jupiter.yml --tags security

# Single role (e.g., just wavebox)
ansible-playbook -K -i hosts jupiter.yml --tags wavebox

# Cloud tools refresh
ansible-playbook -K -i hosts jupiter.yml --tags cloud-tools

# Force key backup on this run
ansible-playbook -K -i hosts jupiter.yml --tags keys -e backup_keys=true

# Skip slow tasks
ansible-playbook -K -i hosts jupiter.yml --skip-tags "slow,verify"
```

---

### 4. Quick Wins (Implement First)

Ordered by impact-to-effort ratio (highest first):

**1. Change all `state: latest` to `state: present` across all roles** [30 minutes, HIGH impact]

This single change eliminates the majority of incremental run time. Every `state: latest`
forces DNF to do a metadata refresh and version comparison across all enabled repositories.
Affected roles: `i3`, `i3blocks`, `nvm`, `podman`, `developer-tools`, `pyenv`, `postgres`,
`rbenv`, `authoring`, `slack` (repo path).

**2. Fix the Zoom role - add rpm pre-check** [10 minutes, HIGH impact]

Without this fix, every run downloads ~130MB. Adding a single `rpm -q zoom` check before
the download eliminates this entirely on incremental runs.

**3. Fix the `st` and `dmenu` make tasks - add binary existence check** [15 minutes, HIGH impact]

Compilation always runs. A `stat` check on the installed binary eliminates this.

**4. Fix pyenv - change `update: yes` to `update: false` on all 3 git clones** [5 minutes, HIGH impact]

Three GitHub round-trips eliminated immediately. One-line change per task.

**5. Fix vim plugins - change `update: true` to `update: false`, remove retry logic** [5 minutes, HIGH impact]

Two GitHub round-trips plus retry machinery eliminated.

**6. Fix nvm npm global installs - add per-package existence check** [20 minutes, HIGH impact]

Eight npm registry round-trips eliminated on incremental runs.

**7. Add tags to all roles systematically** [45 minutes, MEDIUM impact]

Enables sub-5-minute targeted runs. Without consistent tags, `--tags desktop` will not
correctly isolate the desktop roles because many tasks lack any tags.

**8. Fix the `postgres` init guard** [5 minutes, MEDIUM impact]

Replace the broken sentinel file check with a `stat` on the actual PostgreSQL data directory.
This prevents `postgresql-setup --initdb` from running and failing on every run.

**9. Move fact cache to persistent directory** [5 minutes, LOW impact]

Change `fact_caching_connection` from `/tmp/ansible_cache` to
`/home/hexgnu/.cache/ansible/facts` in `ansible.cfg`. Ensures facts survive reboots.

**10. Default `backup_keys` to `false` in keys role** [5 minutes, LOW impact]

Prevents dated backup directories from accumulating and prevents tar/gpg operations from
running on every incremental run.

---

### 5. Implementation Checklist

Listed in recommended implementation order:

```
Phase 1: High-impact, zero-risk changes (estimated: 2 hours)

[ ] 1. developer-tools/tasks/main.yml
        - Change state: latest -> state: present on all 4 dnf tasks
        - Add tags (dev-tools, packages, cli-tools, cloud-tools, rust) to all tasks
        - Gate verify loop behind dev_tools_verify variable

[ ] 2. pyenv/tasks/main.yml
        - Change update: yes -> update: false on all 3 git tasks
        - Change state: latest -> state: present on dependency install
        - Add tags: [pyenv, languages, dev-tools] to all tasks

[ ] 3. vim/tasks/main.yml
        - Change update: true -> update: false on both git tasks
        - Remove retries/delay/until/register from both git tasks
        - Change hexgnu hardcodes to {{ username }}
        - Add tags: [vim, dev-tools] to all tasks

[ ] 4. zoom/tasks/main.yml
        - Add rpm -q zoom pre-check task
        - Gate download, install, and cleanup on zoom_installed.rc != 0
        - Add tags: [zoom, desktop] to all tasks

[ ] 5. i3/tasks/main.yml
        - Change state: latest -> state: present
        - Add tags: [i3, desktop, packages]

[ ] 6. i3blocks/tasks/main.yml
        - Change state: latest -> state: present on build deps
        - Add stat check for /usr/local/bin/i3blocks
        - Gate make and make install on stat result
        - Add tags: [i3blocks, desktop]

[ ] 7. st/tasks/main.yml
        - Add stat check for /usr/local/bin/st
        - Gate make and make install on stat result
        - Change hexgnu hardcodes to {{ username }}
        - Add tags: [st, desktop]

[ ] 8. dmenu/tasks/main.yml
        - Add stat check for /usr/local/bin/dmenu
        - Gate make and make install on stat result
        - Change hexgnu hardcodes to {{ username }}
        - Add tags: [dmenu, desktop]

[ ] 9. nvm/tasks/main.yml
        - Change state: latest -> state: present on dep packages
        - Add npm list pre-check loop for 8 global packages
        - Gate install loop on pre-check results
        - Add claude-code which pre-check, gate install on it
        - Add tags: [nvm, languages, dev-tools, npm] to all tasks

[ ] 10. podman/tasks/main.yml
         - Change state: latest -> state: present on main package install
         - Add when: podman_pull_base_images | default(false) to image pull task
         - Add tags: [podman, containers, packages] to all tasks

Phase 2: Medium-impact changes (estimated: 1.5 hours)

[ ] 11. keys/tasks/main.yml
         - Remove the first ssh_key_check stat loop (openssh_keypair is natively idempotent)
         - Remove when: conditions from openssh_keypair tasks
         - Change backup_keys default to false
         - Add tags: [keys, security] to all tasks

[ ] 12. ssh/tasks/main.yml
         - Add known_hosts pre-check stat before ssh-keyscan lookup
         - Gate ssh-keyscan on pre-check result
         - Add tags: [ssh, security] to all tasks

[ ] 13. postgres/tasks/main.yml
         - Replace broken sentinel file check with stat on /var/lib/pgsql/data/PG_VERSION
         - Gate postgresql-setup on stat result
         - Change state: latest -> state: present
         - Add tags: [postgres, databases]

[ ] 14. rbenv/tasks/main.yml
         - Change update: true -> update: false on both git tasks
         - Add stat check for ~/.rbenv/versions/3.2.2
         - Gate rbenv install on stat result
         - Add full path to rbenv binary in command task
         - Change hexgnu hardcodes to {{ username }}
         - Add tags: [rbenv, languages, dev-tools]

[ ] 15. brave/tasks/main.yml
         - Remove update_cache: yes from install task
         - Add stat pre-check loop for old repo files
         - Gate file removal on stat results
         - Add tags: [brave, desktop, packages]

[ ] 16. flatpak/tasks/main.yml
         - Change state: latest -> state: present
         - Add tags: [flatpak, desktop, packages, music] consistently

[ ] 17. authoring/tasks/main.yml
         - Change state: latest -> state: present
         - Add tags: [authoring, packages]

[ ] 18. nvidia/tasks/main.yml
         - Remove the unconditional dnf makecache task
         - Add tags: [nvidia, drivers, packages, cuda] consistently (already partially done)

[ ] 19. slack/tasks/main.yml
         - Add tags: [slack, desktop, flatpak] consistently

[ ] 20. wavebox/tasks/main.yml
         - Tags already present; ensure all tasks have them (already done in this role)

[ ] 21. 1password/tasks/main.yml
         - Add tags: [1password, security, packages]

[ ] 22. direnv/tasks/main.yml
         - Add tags: [direnv, dev-tools, packages]

Phase 3: Infrastructure changes (estimated: 30 minutes)

[ ] 23. ansible.cfg
         - Change fact_caching_connection from /tmp/ansible_cache to
           /home/hexgnu/.cache/ansible/facts
         - Create the cache directory: file task in setup role or a pre_tasks entry

[ ] 24. jupiter.yml - tasks section
         - Add tags to hostname task: [setup, system]
         - Add tags to sshd task: [setup, system, ssh]
         - Add tags to RPMFusion tasks: [setup, system, repos, personal]

[ ] 25. Makefile - add new targets using the tag taxonomy
         - make quick    -> --tags packages (only package installs)
         - make lang     -> --tags languages
         - make update-desktop -> --tags desktop
         - make keys     -> --tags keys -e backup_keys=true
         - make check-tools -> --tags verify

Phase 4: Cleanup (estimated: 30 minutes)

[ ] 26. install_repos/tasks/main.yml
         - Evaluate whether this role has any valid use cases
         - Either delete the directory or add a comment explaining its orphaned status
         - It is not referenced in jupiter.yml so poses no active harm

[ ] 27. rbenv/tasks/main.yml
         - Evaluate whether rbenv is still needed vs. pyenv for Ruby
         - The role is not referenced in jupiter.yml, making it dead code like install_repos

[ ] 28. docker/tasks/main.yml
         - The role is not referenced in jupiter.yml (podman is used instead)
         - Either remove or annotate as dormant

[ ] 29. Global: audit all remaining hardcoded hexgnu references
         - Replace with {{ username }} throughout all role files
         - Affected: st, dmenu, vim, rbenv
```

---

## Example Usage After Optimization

```bash
# Full provisioning run - fresh Fedora installation (rare, runs everything)
make all

# Quick incremental package state check (~2-3 min, just verifies package presence)
ansible-playbook -K -i hosts jupiter.yml --tags packages

# Update desktop environment (i3, flatpak apps, brave, wavebox, slack, zoom)
ansible-playbook -K -i hosts jupiter.yml --tags desktop

# Update development tools and language managers
ansible-playbook -K -i hosts jupiter.yml --tags dev-tools

# Language version managers only
ansible-playbook -K -i hosts jupiter.yml --tags languages

# Modern CLI tools only (fzf, bat, eza, etc.)
ansible-playbook -K -i hosts jupiter.yml --tags cli-tools

# Cloud tools (Azure CLI, Google Cloud CLI)
ansible-playbook -K -i hosts jupiter.yml --tags cloud-tools

# NVIDIA drivers (when kernel updates break drivers)
make nvidia

# Force SSH/GPG key backup
ansible-playbook -K -i hosts jupiter.yml --tags security -e backup_keys=true

# Single application update
ansible-playbook -K -i hosts jupiter.yml --tags zoom
ansible-playbook -K -i hosts jupiter.yml --tags wavebox
ansible-playbook -K -i hosts jupiter.yml --tags brave

# Skip slow/expensive tasks on a known-good system
ansible-playbook -K -i hosts jupiter.yml --skip-tags "slow,verify,podman_images"

# Dry run to preview changes without applying
make dry-run
```

**Makefile additions to support the tag taxonomy:**
```makefile
# Quick package state check - fastest incremental run
quick:
	@echo "Checking package state (fast incremental run)..."
	ansible-playbook -K -i hosts jupiter.yml --tags packages

# Desktop environment update
update-desktop:
	@echo "Updating desktop environment..."
	ansible-playbook -K -i hosts jupiter.yml --tags desktop

# Language version managers
lang:
	@echo "Updating language version managers..."
	ansible-playbook -K -i hosts jupiter.yml --tags languages

# Security and key management
keys:
	@echo "Running key management with backup..."
	ansible-playbook -K -i hosts jupiter.yml --tags security -e backup_keys=true

# CLI tools update
cli-tools:
	@echo "Updating modern CLI tools..."
	ansible-playbook -K -i hosts jupiter.yml --tags cli-tools

# Cloud development tools
cloud:
	@echo "Updating cloud tools (Azure, GCloud)..."
	ansible-playbook -K -i hosts jupiter.yml --tags cloud-tools
```

---

## Appendix: Detailed Task Analysis - Full Findings Table

| Role | File | Task | Issue | Category | Impact |
|---|---|---|---|---|---|
| i3 | tasks/main.yml | install i3 packages | state: latest | state | HIGH |
| i3blocks | tasks/main.yml | build deps | state: latest | state | HIGH |
| i3blocks | tasks/main.yml | make it / install it | no creates guard | idempotency | HIGH |
| flatpak | tasks/main.yml | install flatpak | state: latest | state | MEDIUM |
| brave | tasks/main.yml | Install Brave browser | update_cache: yes | cache | MEDIUM |
| brave | tasks/main.yml | Remove old repo files | runs unconditionally | idempotency | LOW |
| st | tasks/main.yml | make and install | no existence check | idempotency | HIGH |
| st | tasks/main.yml | all tasks | hardcoded hexgnu | maintainability | LOW |
| vim | tasks/main.yml | install ctrl-p | update: true + retries | git | HIGH |
| vim | tasks/main.yml | install packer | update: true + retries | git | HIGH |
| vim | tasks/main.yml | all tasks | hardcoded hexgnu | maintainability | LOW |
| pyenv | tasks/main.yml | clone pyenv | update: yes | git | HIGH |
| pyenv | tasks/main.yml | clone pyenv-virtualenv | update: yes | git | HIGH |
| pyenv | tasks/main.yml | clone pyenv-update | update: yes | git | HIGH |
| pyenv | tasks/main.yml | install deps | state: latest | state | MEDIUM |
| nvm | tasks/main.yml | install nvm deps | state: latest | state | MEDIUM |
| nvm | tasks/main.yml | claude-code install | no pre-check | idempotency | HIGH |
| nvm | tasks/main.yml | 8 npm global pkgs | no pre-check, always runs | idempotency | HIGH |
| podman | tasks/main.yml | Install Podman | state: latest | state | MEDIUM |
| podman | tasks/main.yml | Pull base images | runs every run | idempotency | MEDIUM |
| developer-tools | tasks/main.yml | Install gh | state: latest | state | HIGH |
| developer-tools | tasks/main.yml | Install azure-cli | state: latest | state | HIGH |
| developer-tools | tasks/main.yml | Install gcloud | state: latest | state | HIGH |
| developer-tools | tasks/main.yml | Install rust | state: latest | state | HIGH |
| developer-tools | tasks/main.yml | Install dev tools | state: latest | state | MEDIUM |
| developer-tools | tasks/main.yml | Install cli tools | state: latest | state | HIGH |
| developer-tools | tasks/main.yml | verify loop (12 cmds) | runs every run | overhead | LOW |
| zoom | tasks/main.yml | Download Zoom RPM | no pre-check, always downloads | idempotency | HIGH |
| rbenv | tasks/main.yml | rbenv clone | update: true | git | HIGH |
| rbenv | tasks/main.yml | ruby-build clone | update: true | git | HIGH |
| rbenv | tasks/main.yml | rbenv install 3.2.2 | no existence check | idempotency | HIGH |
| rbenv | tasks/main.yml | all tasks | hardcoded hexgnu | maintainability | LOW |
| keys | tasks/main.yml | ssh_key_check stat loop | redundant (openssh_keypair is idempotent) | overhead | MEDIUM |
| keys | tasks/main.yml | GPG/SSH backup | runs every run | idempotency | MEDIUM |
| ssh | tasks/main.yml | ensure github known host | live ssh-keyscan on every run | network | MEDIUM |
| ssh | tasks/main.yml | all tasks | no tags | tagging | MEDIUM |
| nvidia | tasks/main.yml | Update repository cache | dnf makecache unconditional | cache | MEDIUM |
| postgres | tasks/main.yml | bootup | broken sentinel file guard | idempotency | MEDIUM |
| postgres | tasks/main.yml | install packages | state: latest | state | MEDIUM |
| authoring | tasks/main.yml | install packages | state: latest | state | MEDIUM |
| dmenu | tasks/main.yml | make dmenu | no existence check | idempotency | MEDIUM |
| dmenu | tasks/main.yml | make install dmenu | no existence check | idempotency | MEDIUM |
| install_repos | tasks/main.yml | Download RPMFusion | Fedora 31 URLs, dead code | dead code | HIGH |
| install_repos | tasks/main.yml | Spotify repo | outdated negativo17 URL | dead code | HIGH |
| jupiter.yml | main playbook | tasks section | no tags | tagging | MEDIUM |
| ansible.cfg | config | fact cache | /tmp path cleared on reboot | caching | LOW |

**Total optimization opportunities identified: 47** (31 unique code changes, 47 individual task issues)

---

## Notes on Roles NOT in jupiter.yml

The following role directories exist in the repository but are NOT referenced in `jupiter.yml`:

- `install_repos/` - Dead code (Fedora 31, outdated URLs)
- `rbenv/` - Not in active playbook (pyenv handles Python; Ruby covered by rbenv but not included)
- `docker/` - Replaced by podman in the active playbook
- `authoring/` - Not in active playbook (no entry in jupiter.yml roles list)
- `postgres/` - Not in active playbook
- `miniconda/` - Not in active playbook (pyenv handles this)
- `ssh/` - Keys role replaced this; ssh/ is legacy
- `wireguard/` - Commented out in jupiter.yml
- `firewall/` - Has a defaults directory but not in jupiter.yml

These roles cannot cause issues during `make all` since they are not included, but they add
confusion and should either be removed or moved to an `archive/` subdirectory.
