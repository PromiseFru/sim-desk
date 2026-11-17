# SPDX-License-Identifier: GPL-3.0-or-later
import itertools
from dataclasses import dataclass, field

import gi
import pytest

gi.require_version("ModemManager", "1.0")
# pygobject-stubs has no ModemManager types.
from gi.repository import GLib, ModemManager  # noqa: E402  # pyright: ignore[reportAttributeAccessIssue]


class FakeGObject:
    def __init__(self):
        self.handlers = {}
        self._handler_ids = itertools.count(1)

    def connect(self, signal, handler):
        handler_id = next(self._handler_ids)
        self.handlers[handler_id] = (signal, handler)
        return handler_id

    def disconnect(self, handler_id):
        del self.handlers[handler_id]

    def emit(self, signal, *args):
        for name, handler in list(self.handlers.values()):
            if name == signal:
                handler(self, *args)


@dataclass
class FakeSim:
    imsi: str = "624010000000001"

    def get_imsi(self):
        return self.imsi


@dataclass
class FakeModemIface(FakeGObject):
    manufacturer: str = "QUALCOMM INCORPORATED"
    model: str = "Snapdragon X55"
    revision: str = "SDX55-1.0"
    state: int = ModemManager.ModemState.REGISTERED
    access_technologies: int = ModemManager.ModemAccessTechnology.LTE
    signal: tuple = (72, True)
    sim_path: str = "/org/freedesktop/ModemManager1/SIM/0"
    sim: FakeSim | None = field(default_factory=FakeSim)
    sim_error: bool = False

    def __post_init__(self):
        FakeGObject.__init__(self)

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

    async def get_sim(self, _cancellable=None):
        if self.sim_error:
            raise GLib.Error("Couldn't read the SIM")
        return self.sim


@dataclass
class Fake3gppIface(FakeGObject):
    imei: str = "860000000000001"
    operator_name: str = "MTN CM"
    operator_code: str = "62401"

    def __post_init__(self):
        FakeGObject.__init__(self)

    def get_imei(self):
        return self.imei

    def get_operator_name(self):
        return self.operator_name

    def get_operator_code(self):
        return self.operator_code


@dataclass
class FakeObject(FakeGObject):
    path: str = "/org/freedesktop/ModemManager1/Modem/0"
    modem: FakeModemIface = field(default_factory=FakeModemIface)
    modem_3gpp: Fake3gppIface | None = field(default_factory=Fake3gppIface)

    def __post_init__(self):
        FakeGObject.__init__(self)

    def get_object_path(self):
        return self.path

    def get_modem(self):
        return self.modem

    def get_modem_3gpp(self):
        return self.modem_3gpp


class FakeMMManager(FakeGObject):
    def __init__(self, objects, name_owner: str | None = ":1.19"):
        super().__init__()
        self.objects = objects
        self.name_owner = name_owner

    def get_objects(self):
        return self.objects

    def get_name_owner(self):
        return self.name_owner


@pytest.fixture
def fake_object():
    return FakeObject()
