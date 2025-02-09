from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pytest
from django.urls import reverse

if TYPE_CHECKING:
    from django.http import HttpResponse
    from django.test import Client

logger: logging.Logger = logging.getLogger(__name__)


@pytest.mark.django_db
def test_index_view(client: Client) -> None:
    """Test index view returns the welcome message."""
    response: HttpResponse = client.get(reverse("index"))
    assert response.status_code == 200
    assert response.content
