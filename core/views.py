from __future__ import annotations

import logging

import sentry_sdk
from django.http import HttpRequest, HttpResponse

logger: logging.Logger = logging.getLogger(__name__)


def index(request: HttpRequest) -> HttpResponse:  # noqa: ARG001
    """Index view.

    Returns:
        HttpResponse: A simple welcome response.
    """
    try:
        return HttpResponse("Welcome to lovinator-space!")
    except Exception as e:
        logger.exception("Error in index view.")
        sentry_sdk.capture_exception(e)
        return HttpResponse("An error occurred.", status=500)
