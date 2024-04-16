import pathlib
from typing import Any

from django.http import HttpRequest
from django.utils import timezone
from django.template.defaultfilters import slugify

from tracker.apps.users.models import User


class TrackerHttpRequest(HttpRequest):
    user: User


class FilenameGenerator:
    def __init__(self, prefix: str) -> None:
        self.prefix = prefix

    def __call__(self, instance: Any, filename: str) -> str:
        today = timezone.localdate()

        filepath = pathlib.Path(filename)
        path = pathlib.Path(
            self.prefix,
            str(today.year),
            str(today.month),
            str(today.day),
            slugify(filepath.stem)
        ).with_suffix(filepath.suffix)

        return path
