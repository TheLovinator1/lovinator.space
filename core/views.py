from __future__ import annotations

import concurrent.futures
import logging
import os
from typing import TYPE_CHECKING, Any

import requests
import sentry_sdk
from django.shortcuts import render

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


logger: logging.Logger = logging.getLogger(__name__)


def fetch_repo_data(repo_def: dict[str, str]) -> dict[str, Any]:
    """Fetches GitHub data for a single repository concurrently.

    Args:
        repo_def (Dict[str, str]): Dictionary with owner and repo keys.

    Returns:
        Dict[str, Any]: Repository data including name, latest commit, and workflows.
    """
    single_repo: dict[str, Any] = {"name": repo_def["repo"], "latest_commit": None, "failed_workflows": None}
    headers: dict[str, str] = {"Accept": "application/vnd.github.v3+json"}

    github_token: str | None = os.getenv("GITHUB_TOKEN")
    if github_token:
        headers["Authorization"] = f"token {github_token}"

    try:
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
    except Exception as e:
        logger.exception("Error retrieving GitHub status for repo %s/%s", repo_def["owner"], repo_def["repo"])
        sentry_sdk.capture_exception(e)
    return single_repo


def index(request: HttpRequest) -> HttpResponse:
    """View to display GitHub repository statuses concurrently.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered HTML with GitHub repository information.
    """
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

    context_repos: list[dict[str, Any]] = []
    try:
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=min(len(repo_list), 10),
            thread_name_prefix="GitHub",
        ) as executor:
            futures: list[concurrent.futures.Future[dict[str, Any]]] = [
                executor.submit(fetch_repo_data, repo_def) for repo_def in repo_list
            ]
            context_repos.extend(future.result() for future in concurrent.futures.as_completed(futures))
    except Exception as e:
        logger.exception("Error processing GitHub repositories concurrently")
        sentry_sdk.capture_exception(e)
    return render(request, "core/index.html", {"repos": context_repos})
