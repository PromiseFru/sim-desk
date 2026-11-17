# SPDX-License-Identifier: GPL-3.0-or-later
from collections.abc import Callable

type Unsubscribe = Callable[[], None]


def subscribe(gobject, signal: str, handler: Callable[..., None]) -> Unsubscribe:
    handler_id = gobject.connect(signal, handler)
    return lambda: gobject.disconnect(handler_id)
