# Pinned rendering environment for the visual regression suite.
# The Playwright version comes from uv.lock via scripts/visual.sh, so the image and the
# locked dependency can never drift apart.
ARG PLAYWRIGHT_VERSION
FROM mcr.microsoft.com/playwright/python:v${PLAYWRIGHT_VERSION}-noble

ARG PLAYWRIGHT_VERSION
# Read back by the collection guard in tests/visual/conftest.py.
ENV VISUAL_PLAYWRIGHT_VERSION=${PLAYWRIGHT_VERSION}

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Keep the virtualenv off the bind-mounted repo, so the host's .venv is never touched.
ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

WORKDIR /app
