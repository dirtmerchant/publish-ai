"""Publisher configuration.

Paths and remotes for the blog repository that the publisher pushes to.
"""

from pathlib import Path

# The blog repo checkout on this machine. The publisher runs git operations
# against this path — it never clones; it assumes the repo is already checked out.
BLOG_REPO_PATH = Path.home() / "repos" / "bertbullough.com"

# Git remote and branch used for publishing.
REMOTE = "origin"
BRANCH = "main"

# Subdirectory inside the blog repo where markdown source lives.
POSTS_DIR = BLOG_REPO_PATH / "posts"
