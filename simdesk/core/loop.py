# SPDX-License-Identifier: GPL-3.0-or-later
import asyncio
from collections.abc import Coroutine

# pygobject-stubs leaves out gi.events, added in PyGObject 3.50.
from gi.events import GLibEventLoop  # pyright: ignore[reportMissingImports]
from gi.repository import GLib


def run[T](coro: Coroutine[object, object, T]) -> T:
    """Runs coro to completion on GLib's default main context."""
    return asyncio.run(
        coro, loop_factory=lambda: GLibEventLoop(GLib.MainContext.default())
    )
