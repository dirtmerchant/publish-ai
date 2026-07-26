#!/usr/bin/env bash
# publish.sh — Confined script for Hermes integration (C-H1).
# Pulls latest from blog repo, runs build.py for local preview, pushes.
#
# This script is the Publisher's only interface to the blog repo.
# It must remain a confined script — never a learned skill.

set -euo pipefail

BLOG_REPO="${HOME}/repos/bertbullough.com"

echo "==> Pulling latest from blog repo..."
git -C "${BLOG_REPO}" pull --ff-only origin main

echo "==> Ensuring blog venv..."
BLOG_VENV="${BLOG_REPO}/.venv"
if [ ! -d "${BLOG_VENV}" ]; then
    /usr/bin/python3 -m venv "${BLOG_VENV}"
    "${BLOG_VENV}/bin/pip" install --quiet -r "${BLOG_REPO}/requirements.txt"
fi

echo "==> Building blog (local preview)..."
"${BLOG_VENV}/bin/python" "${BLOG_REPO}/build.py"

echo "==> Pushing to origin/main..."
git -C "${BLOG_REPO}" push origin main

echo "==> Done. GitHub Actions will deploy."
