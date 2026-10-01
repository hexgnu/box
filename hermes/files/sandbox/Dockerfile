# Hermes terminal-backend sandbox image.
#
# Base is the image hermes uses by default when terminal.docker_image is unset
# (tools/terminal_tool.py:673, hermes_cli/setup_terminal.py:16). Keeping that
# base means nothing about the sandbox changes except the two extra binaries —
# same Debian 13 (trixie), same root default user, same null entrypoint, so
# docker.py's _image_uses_init_entrypoint() still takes the `--init` path and
# the hardened run args in _BASE_SECURITY_ARGS apply unchanged.
#
#   podman build -t localhost/hermes-sandbox:latest hermes/files/sandbox
#   hermes config set terminal.docker_image localhost/hermes-sandbox:latest
#
# Versions are pinned so a rebuild six months from now produces the same image.
# Bump them here (or pass --build-arg) rather than floating on latest.
ARG HIMALAYA_VERSION=2.1.0
ARG ORTIE_VERSION=2.2.0
ARG RUNTIME_IMAGE=docker.io/nikolaik/python-nodejs:python3.11-nodejs20

# ---- builder ------------------------------------------------------------
# NOT `apt-get install rustc cargo`: trixie ships rustc 1.85.1 and himalaya 2.1
# declares rust-version 1.89, so cargo refuses to build it. The rust image is
# trixie-based too, so the glibc these binaries link against matches the runtime
# stage exactly. Non-slim carries buildpack-deps (cc, pkg-config, libssl-dev),
# which is everything the rustls-ring default feature needs.
FROM docker.io/library/rust:1-trixie AS build

ARG HIMALAYA_VERSION
ARG ORTIE_VERSION

# --root /out collects both binaries in one dir to COPY from.
# --locked builds the dependency versions in each crate's shipped Cargo.lock.
RUN cargo install --locked --root /out \
      "himalaya@${HIMALAYA_VERSION}" \
      "ortie@${ORTIE_VERSION}"

# ---- runtime ------------------------------------------------------------
FROM ${RUNTIME_IMAGE}

COPY --from=build /out/bin/himalaya /usr/local/bin/himalaya
COPY --from=build /out/bin/ortie    /usr/local/bin/ortie

# Fail the build, not the agent's first tool call, if a shared lib is missing.
RUN himalaya --version && ortie --version
