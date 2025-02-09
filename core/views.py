from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Any

import requests
import sentry_sdk
from django.shortcuts import render

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

logger: logging.Logger = logging.getLogger(__name__)


def index(request: HttpRequest) -> HttpResponse:
    """View to display GitHub repo statuses including latest commit and broken workflows.

    The view retrieves data for each repository defined in the repo_list, including
    the latest commit and failed workflows. If errors occur when fetching data for a repo,
    the error is logged and sent to Sentry, and processing continues for other repos.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered HTML with GitHub repository information.
    """
    # List of repositories to process.
    # Update this list to add or remove repositories.
    repo_list: list[dict[str, str]] = [
        {"owner": "TheLovinator1", "repo": "ANewDawn"},
        {"owner": "TheLovinator1", "repo": "browser"},
        {"owner": "TheLovinator1", "repo": "discord-embed"},
        {"owner": "TheLovinator1", "repo": "discord-free-game-notifier"},
        {"owner": "TheLovinator1", "repo": "discord-reminder-bot"},
        {"owner": "TheLovinator1", "repo": "discord-rss-bot"},
        {"owner": "TheLovinator1", "repo": "discord-twitter-webhooks"},
        {"owner": "TheLovinator1", "repo": "FeedVault.se"},
        {"owner": "TheLovinator1", "repo": "github-sponsor-discord-notifier"},
        {"owner": "TheLovinator1", "repo": "lovinator.space"},
        {"owner": "TheLovinator1", "repo": "mail-to-discord"},
        {"owner": "TheLovinator1", "repo": "panso.se"},
        {"owner": "TheLovinator1", "repo": "sitemap-parser"},
        {"owner": "TheLovinator1", "repo": "Sunbreeze"},
        {"owner": "TheLovinator1", "repo": "twitch-drop-notifier"},
        {"owner": "TheLovinator1", "repo": "twitch-online-notifier"},
    ]
    github_token: str | None = os.environ.get("GITHUB_TOKEN")
    headers: dict[str, str] = {"Authorization": f"token {github_token}"} if github_token else {}
    context_repos: list[dict[str, Any]] = []

    for repo_def in repo_list:
        single_repo: dict[str, Any] = {
            "owner": repo_def["owner"],
            "repo": repo_def["repo"],
            "latest_commit": None,
            "failed_workflows": [],
        }
        try:
            # Get latest commit for the current repo
            commit_url: str = f"https://api.github.com/repos/{repo_def['owner']}/{repo_def['repo']}/commits"
            commit_resp: requests.Response = requests.get(commit_url, headers=headers, timeout=10)
            commit_resp.raise_for_status()
            commits = commit_resp.json()
            if commits:
                latest = commits[0]
                single_repo["latest_commit"] = {
                    "message": latest.get("commit", {}).get("message", ""),
                    "time": latest.get("commit", {}).get("committer", {}).get("date", ""),
                }

            # Get workflow runs and filter for failed or cancelled workflows
            workflow_url: str = f"https://api.github.com/repos/{repo_def['owner']}/{repo_def['repo']}/actions/runs"
            wf_resp: requests.Response = requests.get(workflow_url, headers=headers, timeout=10)
            wf_resp.raise_for_status()
            workflows = wf_resp.json().get("workflow_runs", [])
            failed = [wf for wf in workflows if wf.get("conclusion") in {"failure", "cancelled"}]
            single_repo["failed_workflows"] = failed

        except Exception as e:
            logger.exception("Error retrieving GitHub status for repo %s/%s", repo_def["owner"], repo_def["repo"])
            sentry_sdk.capture_exception(e)

        context_repos.append(single_repo)

    return render(request, "core/index.html", {"repos": context_repos})
