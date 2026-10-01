# hermes

Provisions [Hermes Agent](https://github.com/NousResearch/hermes-agent) — the
always-on assistant reachable over Telegram, backed by a systemd `--user`
gateway.

```bash
make hermes                       # this role only
ansible-playbook -K -i hosts jupiter.yml --tags hermes --ask-vault-pass
```

## What this role owns

| Thing | How |
|---|---|
| Install | `install.sh` from `hermes-agent.nousresearch.com`, guarded by `creates: ~/.local/bin/hermes` |
| Toolchain | Nothing to do — the installer vendors python, node, npm, uv, ripgrep, ffmpeg and chromium into `~/.hermes/tools/` |
| Updates | `hermes update --yes`, only when `update`/`hermes-update` is in `--tags` |
| Lingering | `loginctl enable-linger` — without it the gateway dies at logout |
| Gateway state | `systemd: scope=user, enabled, started` |
| Skills | `skills.external_dirs` → `~/git/personal/dotfiles/hermes/skills` |
| MCP connectors | `hermes mcp install <name>` for each entry in `hermes_mcp_servers` |
| Sandbox image | `podman build` of `files/sandbox/Dockerfile` → `terminal.docker_image` |

## Sandbox image

The docker terminal backend runs every agent command in a container. `files/sandbox/Dockerfile`
extends hermes' own default base with two Rust CLIs — `himalaya` (email) and `ortie`
(OAuth 2.0 tokens) — so the agent can work mail from inside the sandbox.

```bash
make hermes                                                   # builds only if missing or changed
ansible-playbook -K -i hosts jupiter.yml --tags hermes-sandbox # force a rebuild
podman build -t localhost/hermes-sandbox:latest hermes/files/sandbox  # standalone
```

Three things worth knowing:

**Don't `apt-get install rustc cargo`.** The base is Debian 13 (trixie), which ships
rustc 1.85.1; himalaya 2.1 declares `rust-version = 1.89` and cargo refuses the build.
A `rust:1-trixie` builder stage compiles the binaries and the runtime stage copies them
in — trixie on both sides, so the glibc matches and the final image grows ~21 MB
instead of carrying a toolchain. Cold build is ~4 minutes.

**Build rootless, as `{{ username }}`.** The gateway runs the container rootless, and
rootless podman has its own image store. An image built under `sudo` is invisible to it.

**Versions are pinned** via `ARG HIMALAYA_VERSION` / `ORTIE_VERSION` so a rebuild is
reproducible rather than floating on whatever crates.io serves that day.

Setting `terminal.docker_image` explicitly also settles an upstream disagreement: with
the key unset, `hermes config get terminal.docker_image` reports `python3.14-nodejs22`
(from `hermes_cli/config_defaults.py`) while the container the gateway actually spawns
is `python3.11-nodejs20` (the fallback in `tools/terminal_tool.py:_get_env_config()`).


## Mail credentials in the sandbox

Baking `himalaya` and `ortie` into the image is not enough to send or read mail —
the binaries are there, the credential is not.

Both configs are templated by this role. That is new: they used to be hand-written
files on one host, managed by neither repo, so a reinstall lost them and the task
that built the sandbox config had nothing to read. `token.command` has to reference
role-managed paths anyway, which is why box owns them rather than dotfiles.

The chain on the host:

```
himalaya  imap.sasl.xoauth2.token.command = ["~/.local/bin/ortie","token","show","-a","onevizion"]
ortie     storage.read.command            = ["age","-d","-i",<key>,"~/.hermes/ortie-refresh.age"]
          storage.write.command           = "~/.local/bin/hermes-ortie-store"
```

### Why age and not secret-tool

This was `secret-tool`, i.e. the GNOME keyring. The problem was never encryption —
it was that gnome-keyring is a *session* service. It needs D-Bus, an unlocked
keyring and therefore a graphical login, and the gateway lingers, so this box runs
for days without one. The token export was failing for reasons that had nothing to
do with mail.

`age` is a binary and a keyfile: no agent, no bus, no session, works from boot. Be
clear about what that buys, though — on a single-user box the key sits next to the
ciphertext, so encryption at rest here defends against backups, file-sync accidents
and a stray `cat`, not against something already running as this user. The sandbox
boundary is what defends against that.

`systemd-creds` was the other headless candidate and is the one to avoid: it seals
to the TPM, so it is *more* host-bound than what it would replace.

### Why the refresh token stays on the host

```
host    ortie-refresh.age ──ortie token show──> ~/.hermes/sandbox-secrets/onevizion.token
        (hermes-mail-token.timer, every 20min, write-then-rename)

podman  -v ~/.hermes/sandbox-secrets:/run/secrets:ro,z
        -e HIMALAYA_CONFIG=/run/secrets/himalaya.toml
```

Now that the store is a plain file, a container *could* read it. Two reasons it
does not:

**Rotation has nowhere to land.** Entra returns a new refresh token on every
redemption, and the backend spawns a fresh container per session with
`/run/secrets` mounted read-only. A sandbox refreshing for itself would lose each
new token at container exit and replay a stale one until Entra returned
`invalid_grant`. Making the mount writable fixes that by handing the agent write
access to the credential.

**This agent reads untrusted email**, which is the textbook prompt-injection
vector, and the sandbox exists precisely because agent-driven code is not trusted.
A refresh token in there is a 90-day credential behind a public client-id with no
second factor. Worst case as built is one access token with about an hour to live.

The store is seeded **create-only**, from `vault_hermes_mail_refresh_token` if set,
otherwise migrated out of the keyring once. This matters: after the first rotation
the file is the live source of truth and the vault value is stale, so a task that
re-asserted it every provision would replace a working token with an expired one.
Note also that `group_vars/*/vault.yml` is gitignored — the vault is a local seed,
not a backup.

**`:z`, not `:Z`.** SELinux is enforcing and the backend spawns a fresh container per
session. `Z` assigns a per-container category, so concurrent sandboxes would relabel
the directory out from under each other; `z` uses the shared container label.

```bash
ansible-playbook -K -i hosts jupiter.yml --tags hermes-mail --ask-vault-pass
podman run --rm -v ~/.hermes/sandbox-secrets:/run/secrets:ro,z \
  -e HIMALAYA_CONFIG=/run/secrets/himalaya.toml \
  localhost/hermes-sandbox:latest himalaya mailbox list   # verify
```

## What this role deliberately does NOT own

Two files in `~/.hermes/` are machine-generated and version-pinned. Ansible
manages their *state*, never their *contents* — hermes owns the bytes.

**`config.yaml`** — 124KB, carries `_config_version`, and `hermes update` runs
migrations against it in place. A template would be overwritten on every update
and would fight the migrator. Single keys get poked via `hermes config set`,
which is migration-aware.

**`~/.config/systemd/user/hermes-gateway.service`** — generated by
`hermes gateway setup` with vendored tool versions baked into `Environment=PATH`
(`node-26.7.0-linux-x64`, `npm-12.0.2-linux-x64`, …). Templating those freezes
them, so the unit breaks the first time `hermes update` bumps a toolchain. The
role asserts the unit exists and manages enabled/started; it does not write it.

## Manual steps on a bare-metal rebuild

Four, all interactive. The last task in the role checks for them and prints the
exact command for whichever is missing.

```bash
hermes setup                  # provider + model, writes config.yaml
hermes gateway setup          # Telegram bot token + allowed users -> .env
hermes egress setup           # iron-proxy credential-injection firewall
hermes mcp login todoist      # browser OAuth consent
```

`SOUL.md` (persona) is not generated — it comes from the dotfiles repo via
`dotfiles/hermes/install.sh`.

## Secrets

`~/.hermes/.env` holds `TELEGRAM_BOT_TOKEN` and `FIREWORKS_API_KEY`. It is not
vaulted or templated here; `hermes gateway setup` writes it. If you later want
an unattended rebuild, that file is the one thing to move into ansible-vault.

`group_vars/all/vault.yml` needs one key for this role. **This repo is public**, so
the mailbox address is vaulted even though it is not a credential — a work address
in a public git history is a scraping target and cannot be unpublished:

```yaml
vault_hermes_mail_address: you@example.com
vault_hermes_mail_refresh_token: ""   # optional; omit to migrate from the keyring
```

Without the first, the role fails its opening assert rather than templating
`email = ""` and failing IMAP an hour later.

`~/.hermes/sandbox-secrets/` (0700) holds the exported Outlook access token. It is
generated, never committed, and expires on its own — see *Mail credentials in the
sandbox*.

The refresh token behind it lives in `~/.hermes/ortie-refresh.age`, outside that
directory so it is never inside the bind mount. Two files to preserve across a
rebuild, neither of them reproducible from this repo:

- `~/.config/age/hermes-mail.key` — the only thing that can decrypt the store.
  Regenerating it orphans the ciphertext, and the way back is a browser re-auth.
- `~/.hermes/ortie-refresh.age` — rotated by ortie on every refresh, so the copy
  in ansible-vault (if any) goes stale immediately. Seed value, not a backup.

Losing either costs one `ortie auth -a onevizion`, not a disaster — but it is a
browser round-trip you cannot do unattended.

Todoist needs no secret: the connector is a vendor-hosted remote MCP using
OAuth 2.1 with dynamic client registration, and hermes handles PKCE, token
exchange and refresh itself.
