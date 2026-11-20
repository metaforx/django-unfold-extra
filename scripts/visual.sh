#!/usr/bin/env bash
# Run the visual regression suite in the pinned Playwright container.
# --cms 5.0|5.1 picks the django CMS version and its reference set (default 5.1).
# Extra arguments are passed through to pytest, e.g.:
#   scripts/visual.sh --update-snapshots
#   scripts/visual.sh --cms 5.0 -k filer-root
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
CMS="5.1"
ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-locked) SYNC_FLAG="" ;;
    --cms) CMS="${2:-}"; shift ;;
    --cms=*) CMS="${1#--cms=}" ;;
    *) ARGS+=("$1") ;;
  esac
  shift
done

# Each version is a dependency group in pyproject.toml; uv run needs the same flags or it
# re-syncs the default (5.1) group.
case "${CMS}" in
  5.0) GROUP_FLAGS="--no-group cms51 --group cms50" ;;
  5.1) GROUP_FLAGS="" ;;
  *)
    echo "visual.sh: --cms must be 5.0 or 5.1, got '${CMS}'" >&2
    exit 2
    ;;
esac

echo "visual.sh: playwright ${PLAYWRIGHT_VERSION}, django CMS ${CMS}"
docker build \
  --build-arg "PLAYWRIGHT_VERSION=${PLAYWRIGHT_VERSION}" \
  --tag "${IMAGE}:${PLAYWRIGHT_VERSION}" \
  "${REPO_ROOT}/tests/visual"

docker run --rm \
  --volume "${REPO_ROOT}:/app" \
  --volume "${VENV_VOLUME}-cms${CMS}:/opt/venv" \
  --workdir /app \
  "${IMAGE}:${PLAYWRIGHT_VERSION}" \
  bash -c "uv sync ${SYNC_FLAG} ${GROUP_FLAGS} && uv run ${GROUP_FLAGS} pytest -m visual $(printf '%q ' "${ARGS[@]+"${ARGS[@]}"}")"
