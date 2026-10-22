"""Write each project's latest release version into profile/README.md.

The README marks every version spot with HTML comments:

    <!--v:REPO-->...<!--/v-->          table cell: version linked to its release
    <!--badge:REPO-->...<!--/badge-->  header badge with the version baked in

Versions come from the GitHub API, so the page never depends on a live badge
service. If a lookup fails, the existing value is kept rather than overwritten.
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

OWNER = "retro-trans"
README = Path(__file__).resolve().parent.parent / "profile" / "README.md"
MARKER = re.compile(r"<!--(v|badge):([\w.-]+)-->(.*?)<!--/\1-->", re.S)


def latest_tag(repo):
    req = urllib.request.Request(
        f"https://api.github.com/repos/{OWNER}/{repo}/releases/latest",
        headers={"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"},
    )
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.load(resp)["tag_name"]
        except (OSError, KeyError, ValueError) as err:
            print(f"warning: {repo} (attempt {attempt}): {err}", file=sys.stderr)
            if isinstance(err, urllib.error.HTTPError) and err.code == 404:
                break
            time.sleep(5 * attempt)
    print(f"warning: {repo}: keeping current value", file=sys.stderr)
    return None


def render(kind, repo, tag):
    url = f"https://github.com/{OWNER}/{repo}/releases/latest"
    if kind == "v":
        return f"[`{tag}`]({url})"
    # Static badge: shields.io only draws it, it never calls GitHub.
    version = urllib.parse.quote(tag.replace("-", "--").replace("_", "__"))
    src = (
        f"https://img.shields.io/badge/Retro%20Trans%20app-{version}-ff5fa2"
        "?style=for-the-badge&labelColor=1b1533"
    )
    return f'<a href="{url}"><img alt="Retro Trans app {tag}" src="{src}"></a>'


def main():
    text = README.read_text(encoding="utf-8")
    tags = {}

    def replace(m):
        kind, repo, current = m.groups()
        if repo not in tags:
            tags[repo] = latest_tag(repo)
        tag = tags[repo]
        body = render(kind, repo, tag) if tag else current
        return f"<!--{kind}:{repo}-->{body}<!--/{kind}-->"

    updated = MARKER.sub(replace, text)
    for repo, tag in sorted(tags.items()):
        print(f"{repo}: {tag or 'unchanged (lookup failed)'}")
    if updated != text:
        with README.open("w", encoding="utf-8", newline="\n") as f:
            f.write(updated)
        print("README updated")
    else:
        print("README already current")


if __name__ == "__main__":
    main()
