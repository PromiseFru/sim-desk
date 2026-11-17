# SPDX-License-Identifier: GPL-3.0-or-later
from dataclasses import dataclass, field

import gi
import pytest

gi.require_version("ModemManager", "1.0")
# pygobject-stubs has no ModemManager types.
from gi.repository import GLib, ModemManager  # noqa: E402  # pyright: ignore[reportAttributeAccessIssue]


@dataclass
class FakeSim:
    imsi: str = "624010000000001"

    def get_imsi(self):
        return self.imsi


@dataclass
class FakeModemIface:
    manufacturer: str = "QUALCOMM INCORPORATED"
    model: str = "Snapdragon X55"
    revision: str = "SDX55-1.0"
    state: int = ModemManager.ModemState.REGISTERED
    access_technologies: int = ModemManager.ModemAccessTechnology.LTE
    signal: tuple = (72, True)
    sim_path: str = "/org/freedesktop/ModemManager1/SIM/0"
    sim: FakeSim | None = field(default_factory=FakeSim)
    sim_error: bool = False

    def get_manufacturer(self):
        return self.manufacturer

    def get_model(self):
        return self.model

    def get_revision(self):
        return self.revision

    def get_state(self):
        return self.state

    def get_access_technologies(self):
        return self.access_technologies

    def get_signal_quality(self):
        return self.signal

    def dup_sim_path(self):
        return self.sim_path

    def get_sim_sync(self, _cancellable):
        if self.sim_error:
            raise GLib.Error("Couldn't read the SIM")
        return self.sim


@dataclass
class Fake3gppIface:
    imei: str = "860000000000001"
    operator_name: str = "MTN CM"
    operator_code: str = "62401"

    def get_imei(self):
        return self.imei

    def get_operator_name(self):
        return self.operator_name

    def get_operator_code(self):
        return self.operator_code


@dataclass
class FakeObject:
    path: str = "/org/freedesktop/ModemManager1/Modem/0"
    modem: FakeModemIface = field(default_factory=FakeModemIface)
    modem_3gpp: Fake3gppIface | None = field(default_factory=Fake3gppIface)

    def get_object_path(self):
        return self.path

    def get_modem(self):
        return self.modem

    def get_modem_3gpp(self):
        return self.modem_3gpp


class FakeMMManager:
    def __init__(self, objects):
        self.objects = objects
        self.handlers = {}

    def get_objects(self):
        return self.objects

    def connect(self, signal, handler):
        self.handlers[signal] = handler
        return len(self.handlers)

    def emit(self, signal, obj):
        self.handlers[signal](self, obj)


@pytest.fixture
def fake_object():
    return FakeObject()
