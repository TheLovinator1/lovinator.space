from __future__ import annotations

import logging

import sentry_sdk
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render  # new import

logger: logging.Logger = logging.getLogger(__name__)


def index(request: HttpRequest) -> HttpResponse:
    """Index view.

    Returns:
        HttpResponse: Rendered HTML response.
    """
    try:
        return render(request, "core/index.html")
    except Exception as e:
        logger.exception("Error in index view.")
        sentry_sdk.capture_exception(e)
        return HttpResponse("An error occurred.", status=500)
