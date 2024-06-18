import pathlib
from typing import Any, Union

from django.db.models import QuerySet
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
            self.prefix, str(today.year), str(today.month), str(today.day), slugify(filepath.stem)
        ).with_suffix(filepath.suffix)

        return path


class Paginator:
    def __init__(self, queryset: QuerySet, page_number: Union[str, int] = 1, step: int = 20) -> None:
        try:
            page_number = int(page_number or 1)
        except ValueError:
            page_number = 1

        self.next = None
        self.next_object = None

        stop_index = (page_number * step) + 1
        if page_number > 1:
            start_index = (page_number - 1) * step - 1

            list_queryset = list(queryset[start_index:stop_index])
            self.previous = page_number - 1
            if len(list_queryset):
                self.previous_object = list_queryset[0]
            else:
                self.previous_object = None
            self.objects = list_queryset[1 : step + 1]

            if len(list_queryset) == step + 2:
                self.next_object = list_queryset[-1]
                self.next = page_number + 1

        else:
            self.previous = None
            self.previous_object = None
            start_index = (page_number - 1) * step
            list_queryset = list(queryset[start_index:stop_index])

            if len(list_queryset) > step:
                self.next = page_number + 1
                self.next_object = list_queryset[-1]

            self.objects = list_queryset[0:step]
