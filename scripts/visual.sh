#!/usr/bin/env bash
# Run the visual regression suite in the pinned Playwright container.
# Extra arguments are passed through to pytest, e.g.:
#   scripts/visual.sh --update-snapshots
#   scripts/visual.sh -k filer-root
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="django-unfold-extra-visual"
VENV_VOLUME="django-unfold-extra-visual-venv"

# The image tracks the locked Playwright version, so a dependency bump moves the browser
# too and the references are regenerated deliberately.
PLAYWRIGHT_VERSION="$(
  awk '/^name = "playwright"$/ {found=1; next} found && /^version = / {gsub(/[",]/, "", $3); print $3; exit}' \
    "${REPO_ROOT}/uv.lock"
)"
if [[ -z "${PLAYWRIGHT_VERSION}" ]]; then
  echo "visual.sh: no playwright version found in uv.lock" >&2
  exit 1
fi

# A string, not an array: bash 3.2 (macOS) treats an empty array as unbound under set -u.
SYNC_FLAG="--locked"
ARGS=()
for arg in "$@"; do
  if [[ "${arg}" == "--no-locked" ]]; then
    SYNC_FLAG=""
  else
    ARGS+=("${arg}")
  fi
done

echo "visual.sh: playwright ${PLAYWRIGHT_VERSION}"
docker build \
  --build-arg "PLAYWRIGHT_VERSION=${PLAYWRIGHT_VERSION}" \
  --tag "${IMAGE}:${PLAYWRIGHT_VERSION}" \
  "${REPO_ROOT}/tests/visual"

docker run --rm \
  --volume "${REPO_ROOT}:/app" \
  --volume "${VENV_VOLUME}:/opt/venv" \
  --workdir /app \
  "${IMAGE}:${PLAYWRIGHT_VERSION}" \
  bash -c "uv sync ${SYNC_FLAG} && uv run pytest -m visual $(printf '%q ' "${ARGS[@]+"${ARGS[@]}"}")"
