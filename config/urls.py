from __future__ import annotations

from typing import TYPE_CHECKING

from django.urls import path

from core.views import index

if TYPE_CHECKING:
    from django.urls.resolvers import URLPattern

urlpatterns: list[URLPattern] = [
    path("", index, name="index"),
]
