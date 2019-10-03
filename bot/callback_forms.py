from __future__ import annotations

from typing import MutableSequence, Optional

from .utils import simple_repr


@simple_repr
class CallbackForm:
    DELIMITER = ":"

    def __init__(self, part: str, parts: Optional[MutableSequence[str]] = None):
        self.parts = parts or []
        self.parts.append(part)

    def __str__(self) -> str:
        return self.callback_string

    def __add__(self, part: str) -> CallbackForm:
        return self.extend(part)

    def extend(self, part: str) -> CallbackForm:
        return CallbackForm(part, [*self.parts])

    @property
    def callback_string(self) -> str:
        return self.DELIMITER.join(self.parts)


_filter_choices = CallbackForm("filter")

CHOICE = _filter_choices.extend("choice")
SKIP = _filter_choices.extend("skip")
SKIP_ALL = _filter_choices.extend("skip_all")

_controls = CallbackForm("controls")

PREVIOUS = _controls.extend("previous")
NEXT = _controls.extend("next")

ALL_PICTURES = CallbackForm("all_pics")

_bookmarks = CallbackForm("bookmark")

ADD = _bookmarks.extend("add")
DELETE = _bookmarks.extend("delete")

LIST_SIZES = CallbackForm("list_sizes")

BUY = CallbackForm("buy")
