# SPDX-License-Identifier: GPL-3.0-or-later
import inspect

import pytest

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
    try:
        return len(inspect.signature(method).parameters)
    except ValueError:
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
