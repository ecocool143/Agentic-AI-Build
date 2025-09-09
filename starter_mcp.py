import os
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPO")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

def fetch_github_issues(repo):
    url = f"https://api.github.com/repos/{repo}/issues"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return [issue for issue in response.json() if "pull_request" not in issue]
    else:
        print("Failed to fetch issues:", response.status_code)
        return []

def summarize_text(text):
    # Simplified summarization if OpenAI is unavailable
    return text.split(".")[0] + "." if text else "No summary available."

def post_to_slack(message):
    # Replace this with real Slack webhook logic if desired
    print("SLACK POST:\n", message)

if __name__ == "__main__":
    issues = fetch_github_issues(REPO)
    print(f"Fetched {len(issues)} issues\n")

    slack_message = "*GitHub Issue Summaries:*\n"
    for i, issue in enumerate(issues, start=1):
        summary = summarize_text(issue["body"])
        print(f"{i}. {issue['title']}")
        print(f"Summary: {summary}\n{'-'*40}")
        slack_message += f"*{i}. {issue['title']}*\n{summary}\n\n"

    post_to_slack(slack_message)
