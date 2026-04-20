#!/usr/bin/env python3
"""
DreamCar Audience Dashboard — refresh pipeline.

Runs the full pipeline:
1. Fetch comments from Instagram post DXV7u2TjEe4 via public GraphQL endpoint
2. Run analyze.py to normalize and aggregate
3. Run build_dashboard.py to regenerate index.html
4. Commit and push to GitHub

Usage:
    python3 refresh.py            # full pipeline
    python3 refresh.py --fetch-only  # only fetch comments.json
    python3 refresh.py --no-push     # skip git commit/push
"""
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import urllib.request as _urlreq
    import urllib.parse as _urlparse
except ImportError:
    sys.exit("urllib not available")

ROOT = Path(__file__).resolve().parent
SHORTCODE = "DXV7u2TjEe4"
MEDIA_ID = "3860759555043262443"
APP_ID = "936619743392459"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
)


def fetch_graphql_comments():
    """Try Instagram's public web GraphQL endpoint for comments pagination."""
    all_parents = []
    after = None
    query_hash = "bc3296d1ce80a24b1b6e40b1e72903f5"
    for page in range(1, 50):  # safety cap
        variables = {"shortcode": SHORTCODE, "first": 50}
        if after:
            variables["after"] = after
        url = (
            "https://www.instagram.com/graphql/query/"
            f"?query_hash={query_hash}"
            f"&variables={_urlparse.quote(json.dumps(variables))}"
        )
        req = _urlreq.Request(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "X-IG-App-ID": APP_ID,
                "Accept": "application/json",
            },
        )
        try:
            with _urlreq.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"[fetch] page {page}: {e}", file=sys.stderr)
            return None
        media = (
            data.get("data", {})
            .get("shortcode_media", {})
            or {}
        )
        edge = media.get("edge_media_to_parent_comment", {})
        edges = edge.get("edges", [])
        if not edges and page == 1:
            return None
        for e in edges:
            n = e["node"]
            all_parents.append(
                {
                    "u": n.get("owner", {}).get("username", ""),
                    "t": n.get("text", ""),
                    "l": n.get("edge_liked_by", {}).get("count", 0),
                    "rc": n.get("edge_threaded_comments", {})
                    .get("count", 0),
                }
            )
        page_info = edge.get("page_info", {})
        if not page_info.get("has_next_page"):
            break
        after = page_info.get("end_cursor")
        time.sleep(1)
    return all_parents


def run(cmd, check=True):
    print(f"[run] {cmd}", file=sys.stderr)
    return subprocess.run(
        cmd, shell=True, cwd=ROOT, check=check,
        capture_output=True, text=True,
    )


def git_push(message=None):
    if message is None:
        message = f"chore: auto-refresh {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    # ensure we're on a branch
    run("git add index.html analysis.json comments.json", check=False)
    diff = subprocess.run(
        "git diff --cached --quiet", shell=True, cwd=ROOT
    )
    if diff.returncode == 0:
        print("[git] nothing to commit", file=sys.stderr)
        return
    run(f'git commit -m "{message}"')
    run("git push origin main")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch-only", action="store_true")
    ap.add_argument("--no-push", action="store_true")
    ap.add_argument("--skip-fetch", action="store_true",
                    help="skip fetching, reuse existing comments.json")
    args = ap.parse_args()

    os.chdir(ROOT)

    if not args.skip_fetch:
        print("[1/3] Fetching comments from Instagram...", file=sys.stderr)
        comments = fetch_graphql_comments()
        if comments is None or len(comments) < 50:
            print(
                f"[fetch] failed or too few comments ({len(comments) if comments else 0}). "
                "Instagram likely requires an authenticated session. "
                "Open the post in a browser-enabled agent and retry.",
                file=sys.stderr,
            )
            if args.fetch_only:
                sys.exit(2)
            # keep going with existing comments.json if present
            if not (ROOT / "comments.json").exists():
                sys.exit(2)
        else:
            (ROOT / "comments.json").write_text(
                json.dumps(comments, ensure_ascii=False, separators=(",", ":"))
            )
            print(f"[fetch] saved {len(comments)} comments", file=sys.stderr)

    if args.fetch_only:
        return

    print("[2/3] Running analyze.py...", file=sys.stderr)
    r = run("python3 analyze.py")
    if r.stdout:
        print(r.stdout)
    if r.stderr:
        print(r.stderr, file=sys.stderr)

    print("[3/3] Running build_dashboard.py...", file=sys.stderr)
    r = run("python3 build_dashboard.py")
    if r.stdout:
        print(r.stdout)

    if not args.no_push:
        git_push()


if __name__ == "__main__":
    main()
