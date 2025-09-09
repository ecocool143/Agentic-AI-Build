import os
import requests
from typing import List, Dict

def fetch_github_issues(repo: str) -> List[Dict]:
    """
    Fetch all issues (state=all) from the given repo and return a list of dicts:
    { number, title, body, html_url }. Pull requests are filtered out.
    """
    assert repo, "GITHUB_REPO must be set in .env"

    token = os.getenv("GITHUB_TOKEN")  
    headers = {
        "Accept": "application/vnd.github+json",
        **({"Authorization": f"token {token}"} if token else {}),
    }

    issues: List[Dict] = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{repo}/issues"
        params = {"state": "all", "per_page": 100, "page": page}
        resp = requests.get(url, headers=headers, params=params, timeout=30)

        # fail fast with clear messaging
        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            raise SystemExit(
                f"GitHub API error ({resp.status_code}). "
                f"Check GITHUB_REPO={repo} and token scope. Details: {e}"
            )

        data = resp.json()
        if not isinstance(data, list):
            raise SystemExit("Unexpected GitHub response format (not a list).")

        # filter out PRs
        only_issues = [it for it in data if "pull_request" not in it]

        # keep the fields we actually use downstream
        for it in only_issues:
            issues.append({
                "number": it.get("number"),
                "title": it.get("title") or "",
                "body": it.get("body") or "",
                "html_url": it.get("html_url") or "",
            })

        # stop paginating when the page is not full
        if len(data) < 100:
            break
        page += 1

    return issues


def summarize_text(text: str) -> str:
    """
    Simple, deterministic fallback summary for Part 3 testing.
    (OpenAI integration is Part 3.5/4 territory; not required to pass Part 3.)
    """
    if not text:
        return "No description provided."
    # take first sentence-ish (up to first period) or first 220 chars
    dot = text.find(".")
    snippet = text[: dot + 1] if dot != -1 else text[:220]
    return snippet.strip() if snippet.strip() else text[:220].strip()


def post_to_slack(message: str) -> None:
    # stub for now
    print("SLACK POST (stub):\n", message)


if __name__ == "__main__":
    # load .env only when running the script directly
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        # if python-dotenv isn't installed yet, Part 2 will have you install it.
        pass

    repo = os.getenv("GITHUB_REPO")
    issues = fetch_github_issues(repo)

    print(f"Fetched {len(issues)} issues\n")

    # print titles + bodies (trimmed) to satisfy Part 3 verification
    for i in issues:
        body_preview = (i["body"] or "").replace("\r", " ").replace("\n", " ").strip()
        if len(body_preview) > 240:
            body_preview = body_preview[:240] + "…"

        print(f"#{i['number']} — {i['title']}")
        print(body_preview if body_preview else "(no body)")
        print("-" * 60)

    # optional: show a quick Slack-style rollup (not required for Part 3)
    rollup = ["*GitHub Issue Summaries (preview)*"]
    for idx, it in enumerate(issues[:5], start=1):
        rollup.append(f"*{idx}. {it['title']}*\n{summarize_text(it['body'])}\n<{it['html_url']}|View on GitHub>")
    post_to_slack("\n\n".join(rollup))

