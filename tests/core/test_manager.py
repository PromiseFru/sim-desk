# SPDX-License-Identifier: GPL-3.0-or-later
import pytest
from gi.repository import Gio, GLib

from simdesk.core.loop import run
from simdesk.core.manager import Manager, ModemManagerUnavailableError
from tests.conftest import FakeMMManager


def test_modems_lists_every_modem_object(fake_object):
    manager = Manager(FakeMMManager([fake_object]))

    assert manager.modems() == [fake_object]


def test_on_modem_added_passes_the_new_modem(fake_object):
    mm_manager = FakeMMManager([])
    added = []
    Manager(mm_manager).on_modem_added(added.append)

    mm_manager.emit("object-added", fake_object)

    assert added == [fake_object]


def test_on_modem_removed_passes_the_object_path(fake_object):
    mm_manager = FakeMMManager([fake_object])
    removed = []
    Manager(mm_manager).on_modem_removed(removed.append)

    mm_manager.emit("object-removed", fake_object)

    assert removed == ["/org/freedesktop/ModemManager1/Modem/0"]


def test_unsubscribing_stops_modem_added_callbacks(fake_object):
    mm_manager = FakeMMManager([])
    added = []
    unsubscribe = Manager(mm_manager).on_modem_added(added.append)

    unsubscribe()
    mm_manager.emit("object-added", fake_object)

    assert added == []


def test_on_daemon_changed_passes_whether_modemmanager_runs():
    mm_manager = FakeMMManager([])
    running = []
    Manager(mm_manager).on_daemon_changed(running.append)

    mm_manager.name_owner = None
    mm_manager.emit("notify::name-owner", None)
    mm_manager.name_owner = ":1.20"
    mm_manager.emit("notify::name-owner", None)

    assert running == [False, True]


def test_connect_reports_an_unreachable_bus(monkeypatch):
    async def fail(*_args):
        raise GLib.Error("Could not connect: No such file or directory")

    monkeypatch.setattr(Gio, "bus_get", fail)

    with pytest.raises(ModemManagerUnavailableError, match="No such file"):
        run(Manager.connect())


def test_connect_reports_a_stopped_daemon():
    bus = Gio.TestDBus.new(Gio.TestDBusFlags.NONE)
    bus.up()
    try:
        address = bus.get_bus_address()
        assert address is not None
        connection = Gio.DBusConnection.new_for_address_sync(
            address,
            Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT
            | Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION,
            None,
            None,
        )
        with pytest.raises(ModemManagerUnavailableError, match="not running"):
            run(Manager.connect(connection))
    finally:
        bus.down()
