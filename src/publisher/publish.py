"""Publisher — commits and pushes post changes to the blog repo.

This is the restricted-action component (C-H1): it only operates on the
blog repo, never on publish-ai's own code. Credentials are scoped to the
blog repo only.
"""

import subprocess
from pathlib import Path

from .config import BLOG_REPO_PATH, BRANCH, POSTS_DIR, REMOTE


def _git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a git command in the blog repo."""
    return subprocess.run(
        ["git", "-C", str(BLOG_REPO_PATH), *args],
        capture_output=True,
        text=True,
        check=check,
    )


def post_path(slug: str) -> Path:
    """Return the filesystem path for a post's markdown source."""
    matches = list(POSTS_DIR.glob(f"*-{slug}.md"))
    if matches:
        return matches[0]
    return POSTS_DIR / f"{slug}.md"


def commit_post(slug: str, message: str | None = None) -> str:
    """Stage and commit a single post file. Returns the commit hash."""
    path = post_path(slug)
    if not path.exists():
        raise FileNotFoundError(f"Post not found: {path}")

    rel = path.relative_to(BLOG_REPO_PATH)
    _git("add", str(rel))

    msg = message or f"publish: {slug}"
    _git("commit", "-m", msg)

    result = _git("rev-parse", "HEAD")
    return result.stdout.strip()


def push() -> None:
    """Push committed changes to the blog remote."""
    _git("push", REMOTE, BRANCH)
