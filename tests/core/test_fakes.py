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
        inputs = [
            a for a in method.get_arguments() if a.get_direction() != Direction.OUT
        ]
        return int(method.is_method()) + len(inputs)
    if isinstance(method, FunctionType):
        return len(inspect.signature(method).parameters)
    return None


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


def test_parameter_count_counts_self_and_skips_out_arguments():
    assert _parameter_count(ModemManager.Modem.get_signal_quality) == 1
