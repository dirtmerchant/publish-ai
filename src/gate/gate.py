"""Verification gate — CLI for human-in-the-loop approval of blog posts.

This is the C-H1 component: it sits OUTSIDE the learning loop. It is a
confined script that must never become a learned skill or be self-rewritten.

Usage:
    python -m src.gate.gate list
    python -m src.gate.gate review <slug>
    python -m src.gate.gate approve <slug>
    python -m src.gate.gate reject <slug>
    python -m src.gate.gate publish
"""

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

from ..publisher.config import BLOG_REPO_PATH, POSTS_DIR

AUDIT_LOG = Path(__file__).resolve().parent.parent.parent / "audit.log"
PUBLISH_SCRIPT = Path(__file__).resolve().parent.parent.parent / "scripts" / "publish.sh"


def _log_action(action: str, slug: str) -> None:
    """Append an action to the audit log."""
    ts = datetime.now(timezone.utc).isoformat()
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(f"{ts}\t{action}\t{slug}\n")


def _find_posts(status_filter: str | None = None) -> list[dict]:
    """Find all posts, optionally filtered by status."""
    posts = []
    if not POSTS_DIR.exists():
        return posts

    for md_file in sorted(POSTS_DIR.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        parts = text.split("---", 2)
        if len(parts) < 3:
            continue
        meta = yaml.safe_load(parts[1])
        if not meta:
            continue
        status = meta.get("status", "draft")
        if status_filter and status != status_filter:
            continue
        posts.append({
            "file": md_file,
            "title": meta.get("title", md_file.stem),
            "slug": meta.get("slug", md_file.stem),
            "date": meta.get("date"),
            "status": status,
            "tags": meta.get("tags", []),
        })
    return posts


def _update_status(md_file: Path, new_status: str) -> None:
    """Rewrite a post's frontmatter status field."""
    text = md_file.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"Invalid frontmatter in {md_file}")

    meta = yaml.safe_load(parts[1])
    meta["status"] = new_status

    # Rebuild the file preserving the body
    new_frontmatter = yaml.dump(meta, default_flow_style=False, sort_keys=False).strip()
    new_text = f"---\n{new_frontmatter}\n---\n{parts[2]}"
    md_file.write_text(new_text, encoding="utf-8")


def cmd_list(args: argparse.Namespace) -> None:
    """List posts by status."""
    status = getattr(args, "status", None) or "draft"
    posts = _find_posts(status_filter=status)
    if not posts:
        print(f"No posts with status '{status}'.")
        return
    for p in posts:
        print(f"  [{p['status']}]  {p['slug']:30s}  {p['title']}")


def cmd_review(args: argparse.Namespace) -> None:
    """Display a post's content for human inspection."""
    posts = _find_posts()
    match = [p for p in posts if p["slug"] == args.slug]
    if not match:
        print(f"Post not found: {args.slug}", file=sys.stderr)
        sys.exit(1)

    post = match[0]
    text = post["file"].read_text(encoding="utf-8")

    print(f"--- {post['title']} ---")
    print(f"Status: {post['status']}")
    print(f"Date:   {post['date']}")
    print(f"Tags:   {', '.join(post['tags'])}")
    print()
    # Print body (everything after the second ---)
    parts = text.split("---", 2)
    if len(parts) >= 3:
        print(parts[2].strip())


def cmd_approve(args: argparse.Namespace) -> None:
    """Approve a post: flip status from draft to published, commit."""
    posts = _find_posts()
    match = [p for p in posts if p["slug"] == args.slug]
    if not match:
        print(f"Post not found: {args.slug}", file=sys.stderr)
        sys.exit(1)

    post = match[0]
    if post["status"] == "published":
        print(f"Already published: {args.slug}")
        return

    _update_status(post["file"], "published")
    _log_action("approve", args.slug)

    # Commit the status change in the blog repo
    rel = post["file"].relative_to(BLOG_REPO_PATH)
    subprocess.run(
        ["git", "-C", str(BLOG_REPO_PATH), "add", str(rel)],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(BLOG_REPO_PATH), "commit", "-m", f"approve: {args.slug}"],
        check=True,
    )
    print(f"Approved and committed: {args.slug}")


def cmd_reject(args: argparse.Namespace) -> None:
    """Reject a post: flip status to rejected."""
    posts = _find_posts()
    match = [p for p in posts if p["slug"] == args.slug]
    if not match:
        print(f"Post not found: {args.slug}", file=sys.stderr)
        sys.exit(1)

    post = match[0]
    _update_status(post["file"], "rejected")
    _log_action("reject", args.slug)

    # Commit the status change
    rel = post["file"].relative_to(BLOG_REPO_PATH)
    subprocess.run(
        ["git", "-C", str(BLOG_REPO_PATH), "add", str(rel)],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(BLOG_REPO_PATH), "commit", "-m", f"reject: {args.slug}"],
        check=True,
    )
    print(f"Rejected: {args.slug}")


def cmd_publish(args: argparse.Namespace) -> None:
    """Run the publish script to push to the blog repo."""
    if not PUBLISH_SCRIPT.exists():
        print(f"Publish script not found: {PUBLISH_SCRIPT}", file=sys.stderr)
        sys.exit(1)

    result = subprocess.run(
        ["bash", str(PUBLISH_SCRIPT)],
        capture_output=False,
    )
    sys.exit(result.returncode)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verification gate for blog publishing (C-H1)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list
    sp_list = subparsers.add_parser("list", help="Show posts by status")
    sp_list.add_argument("--status", default="draft", help="Filter by status (default: draft)")
    sp_list.set_defaults(func=cmd_list)

    # review
    sp_review = subparsers.add_parser("review", help="Display post content for inspection")
    sp_review.add_argument("slug", help="Post slug to review")
    sp_review.set_defaults(func=cmd_review)

    # approve
    sp_approve = subparsers.add_parser("approve", help="Approve a post for publishing")
    sp_approve.add_argument("slug", help="Post slug to approve")
    sp_approve.set_defaults(func=cmd_approve)

    # reject
    sp_reject = subparsers.add_parser("reject", help="Reject a post")
    sp_reject.add_argument("slug", help="Post slug to reject")
    sp_reject.set_defaults(func=cmd_reject)

    # publish
    sp_publish = subparsers.add_parser("publish", help="Push approved posts to the blog repo")
    sp_publish.set_defaults(func=cmd_publish)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
