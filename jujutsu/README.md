# Jujutsu Ansible Role

Installs [Jujutsu](https://github.com/jj-vcs/jj) (`jj`), a Git-compatible VCS.

## What it Does

1. **Installs the `jj` binary** to `/usr/local/bin/jj` from the upstream GitHub
   release tarball (`x86_64-unknown-linux-musl`). Jujutsu is not packaged in
   Fedora 42, so this follows the same GitHub-release pattern used for `eza`
   and `lazygit` in the `developer-tools` role.
2. **Installs the bash completion script** to
   `/usr/share/bash-completion/completions/jj`.
3. **Does NOT configure `jj`** — user config (`~/.config/jj/config.toml`,
   aliases, shell integration) belongs in dotfiles.

## Installation

```bash
make jj          # this role only
make all         # full playbook
```

## Upgrading

Bump `jujutsu_version` in `defaults/main.yml` and rerun `make jj`. The role
compares the installed `jj --version` against that value, reinstalls when they
differ, and regenerates the completion script.

## Variables

| Variable                | Default                  | Description                      |
|-------------------------|--------------------------|----------------------------------|
| `jujutsu_version`       | `0.46.0`                 | Release version to install       |
| `jujutsu_install_path`  | `/usr/local/bin/jj`      | Binary destination               |
| `jujutsu_archive_url`   | derived from version     | Release tarball URL              |
| `jujutsu_completion_dir`| `/usr/share/bash-completion/completions` | Completion script dir |

## Usage Notes

`jj` colocates with Git, so existing repos work without migration:

```bash
cd ~/git/personal/box
jj git init --colocate
```
