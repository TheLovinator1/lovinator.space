from __future__ import annotations

import logging
import os
from typing import Any, LiteralString

import requests
import sentry_sdk
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

logger: logging.Logger = logging.getLogger(__name__)


def index(request: HttpRequest) -> HttpResponse:
    """View to display GitHub repo status including latest commit and broken workflows.

    Returns:
        HttpResponse: Rendered HTML with GitHub information.
    """
    owner = "TheLovinator1"
    repo = "ANewDawn"
    github_token: str | None = os.environ.get("GITHUB_TOKEN")
    headers: dict[str, str] = {"Authorization": f"token {github_token}"} if github_token else {}

    context: dict[str, Any] = {"latest_commit": None, "failed_workflows": []}
    try:
        # Get latest commit
        commit_url: LiteralString = f"https://api.github.com/repos/{owner}/{repo}/commits"
        commit_resp: requests.Response = requests.get(commit_url, headers=headers, timeout=10)
        commit_resp.raise_for_status()
        commits = commit_resp.json()
        if commits:
            latest = commits[0]
            context["latest_commit"] = {
                "message": latest.get("commit", {}).get("message", ""),
                "time": latest.get("commit", {}).get("committer", {}).get("date", ""),
            }

        # Get workflow runs and filter broken runs (e.g. those that failed or were cancelled)
        workflow_url: LiteralString = f"https://api.github.com/repos/{owner}/{repo}/actions/runs"
        wf_resp: requests.Response = requests.get(workflow_url, headers=headers, timeout=10)
        wf_resp.raise_for_status()
        workflows = wf_resp.json().get("workflow_runs", [])
        failed = [wf for wf in workflows if wf.get("conclusion") in {"failure", "cancelled"}]
        context["failed_workflows"] = failed

        return render(request, "core/index.html", context)
    except Exception as e:
        logger.exception("Error retrieving GitHub status.")
        sentry_sdk.capture_exception(e)
        return HttpResponse("An error occurred while fetching GitHub status.", status=500)
