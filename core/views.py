from __future__ import annotations

import concurrent.futures
import logging
import os
from datetime import datetime
from typing import TYPE_CHECKING, Any

import sentry_sdk
from django.shortcuts import render
from requests_cache import CachedResponse, CachedSession, OriginalResponse

if TYPE_CHECKING:
    import requests
    from django.http import HttpRequest, HttpResponse


logger: logging.Logger = logging.getLogger(__name__)


def github_request(url: str) -> dict[str, Any]:
    """Helper function to make authenticated requests to GitHub API.

    Args:
        url (str): The GitHub API URL to request.

    Returns:
        dict[str, Any]: JSON response from GitHub API, or an empty dict on failure.
    """
    session: requests.Session = CachedSession("github_cache", expire_after=300)
    headers: dict[str, str] = {"Accept": "application/vnd.github.v3+json"}

    github_token: str | None = os.getenv("GITHUB_TOKEN")
    if github_token:
        headers["Authorization"] = f"token {github_token}"

    try:
        response: OriginalResponse | CachedResponse = session.get(url, headers=headers, timeout=10)  # pyright: ignore[reportUnknownMemberType]
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.exception("Error retrieving data from GitHub: %s", url)
        sentry_sdk.capture_exception(e)
        return {}


def fetch_repo_data(repo_def: dict[str, str]) -> dict[str, Any]:
    """Fetches GitHub data for a single repository concurrently.

    Args:
        repo_def (dict[str, str]): Dictionary with owner and repo keys.

    Returns:
        dict[str, Any]: Repository data including name, latest commit, and workflows.
    """
    single_repo: dict[str, Any] = {"name": repo_def["repo"], "latest_commit": None, "failed_workflows": None}

    commit_url: str = f"https://api.github.com/repos/{repo_def['owner']}/{repo_def['repo']}/commits"
    commits_response: Any = github_request(commit_url)
    if not commits_response or not isinstance(commits_response, list):
        return single_repo

    latest: Any = commits_response[0]
    single_repo["latest_commit"] = {
        "message": latest.get("commit", {}).get("message", ""),
        "time": datetime.fromisoformat(
            latest.get("commit", {}).get("committer", {}).get("date", "").replace("Z", "+00:00"),
        )
        if latest.get("commit", {}).get("committer", {}).get("date")
        else None,
    }

    status_url: str = f"https://api.github.com/repos/{repo_def['owner']}/{repo_def['repo']}/actions/runs"
    status_data: dict[str, Any] = github_request(status_url)

    workflows = [
        {
            "id": workflow["id"],
            "name": workflow["name"],
            "html_url": workflow["html_url"],
            "created_at": datetime.fromisoformat(workflow["created_at"].replace("Z", "+00:00")),
            "head_branch": workflow["head_branch"],
        }
        for workflow in status_data.get("workflow_runs", [])
        if workflow["conclusion"] in {"failure", "timed_out", "cancelled", "action_required"}
    ]

    single_repo["failed_workflows"] = workflows or None

    return single_repo


def index(request: HttpRequest) -> HttpResponse:
    """View to display GitHub repository statuses concurrently and the current API rate limit.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered HTML with GitHub repository information and API rate limit.
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

    # Sort repositories by name
    context_repos.sort(key=lambda x: x["name"].lower())

    return render(request, "core/index.html", {"repos": context_repos})
