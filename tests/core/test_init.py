# SPDX-License-Identifier: GPL-3.0-or-later
import importlib

import gi
import pytest

import simdesk.core


def test_importing_the_core_on_old_pygobject_fails(monkeypatch):
    monkeypatch.setattr(gi, "version_info", (3, 48, 2), raising=False)

    with pytest.raises(ImportError, match=r"3\.50 or newer, not"):
        importlib.reload(simdesk.core)
