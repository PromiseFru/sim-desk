# SPDX-License-Identifier: GPL-3.0-or-later
import inspect
from types import FunctionType

import pytest

# pygobject-stubs leaves out gi._gi, PyGObject's introspection module.
from gi._gi import Direction  # pyright: ignore[reportMissingImports]

# pygobject-stubs has no ModemManager types.
from gi.repository import ModemManager  # pyright: ignore[reportAttributeAccessIssue]

from tests.conftest import (
    Fake3gppIface,
    FakeGObject,
    FakeMMManager,
    FakeModemIface,
    FakeObject,
    FakeSim,
)

FAKES = [
    (FakeObject, ModemManager.Object),
    (FakeModemIface, ModemManager.Modem),
    (Fake3gppIface, ModemManager.Modem3gpp),
    (FakeSim, ModemManager.Sim),
    (FakeMMManager, ModemManager.Manager),
]


def _parameter_count(method):
    if hasattr(method, "get_arguments"):
        return int(method.is_method()) + len(_python_arguments(method))
    if isinstance(method, FunctionType):
        return len(inspect.signature(method).parameters)
    return None


def _python_arguments(method):
    """Returns the arguments a Python call passes, as an awaited async call passes them.

    Python leaves out output arguments, array lengths, and callbacks with their user
    data and destroy notifiers.
    """
    arguments = method.get_arguments()
    hidden = set()
    for index, argument in enumerate(arguments):
        if argument.get_direction() == Direction.OUT:
            hidden.add(index)
        if argument.get_scope():
            hidden |= {
                index,
                _call(argument, "get_closure_index", "get_closure"),
                _call(argument, "get_destroy_index", "get_destroy"),
            }
        type_info = _call(argument, "get_type_info", "get_type")
        hidden.add(_call(type_info, "get_array_length_index", "get_array_length"))
    return [a for i, a in enumerate(arguments) if i not in hidden]


def _call(info, name, old_name):
    # PyGObject 3.50 has only the old names.
    return (getattr(info, name, None) or getattr(info, old_name))()


@pytest.mark.parametrize(("fake", "real"), FAKES, ids=lambda c: c.__name__)
def test_fake_methods_match_the_real_names_and_parameter_counts(fake, real):
    mismatched = [
        name
        for name, method in inspect.getmembers(fake, inspect.isfunction)
        if not name.startswith("_")
        and (
            not hasattr(real, name)
            or _parameter_count(getattr(real, name))
            not in {None, _parameter_count(method)}
        )
    ]

    assert mismatched == []


@pytest.mark.parametrize(
    ("method", "count"),
    [
        (ModemManager.Modem.get_signal_quality, 1),  # self, not the out argument
        (ModemManager.Modem.get_sim, 2),  # self, cancellable, not callback or data
        (ModemManager.Modem3gpp.set_carrier_lock_sync, 3),  # not the array length
    ],
    ids=lambda v: getattr(v, "__name__", str(v)),
)
def test_parameter_count_matches_what_python_takes(method, count):
    assert _parameter_count(method) == count


def test_fake_handler_ids_stay_unique_after_a_disconnect():
    gobject = FakeGObject()
    calls = []
    first = gobject.connect("changed", lambda _obj: calls.append("first"))
    gobject.connect("changed", lambda _obj: calls.append("second"))
    gobject.disconnect(first)
    gobject.connect("changed", lambda _obj: calls.append("third"))

    gobject.emit("changed")

    assert calls == ["second", "third"]
