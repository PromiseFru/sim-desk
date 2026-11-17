# SPDX-License-Identifier: GPL-3.0-or-later
import pytest

# pygobject-stubs has no ModemManager types.
from gi.repository import ModemManager  # pyright: ignore[reportAttributeAccessIssue]

from simdesk.core.loop import run
from simdesk.core.modem import (
    MODEM_3GPP_PROPERTIES,
    MODEM_PROPERTIES,
    read_info,
    watch,
)
from tests.conftest import Fake3gppIface


def test_info_reads_identity_network_and_signal(fake_object):
    info = run(read_info(fake_object))

    assert info.path == "/org/freedesktop/ModemManager1/Modem/0"
    assert info.manufacturer == "QUALCOMM INCORPORATED"
    assert info.model == "Snapdragon X55"
    assert info.revision == "SDX55-1.0"
    assert info.imei == "860000000000001"
    assert info.imsi == "624010000000001"
    assert info.state == "registered"
    assert info.operator_name == "MTN CM"
    assert info.operator_code == "62401"
    assert info.access_technologies == "lte"
    assert info.signal_quality == 72
    assert info.signal_recent is True


def test_info_without_sim_has_no_imsi(fake_object):
    fake_object.modem.sim_path = "/"

    assert run(read_info(fake_object)).imsi is None


def test_info_when_sim_read_fails_has_no_imsi(fake_object):
    fake_object.modem.sim_error = True

    assert run(read_info(fake_object)).imsi is None


def test_info_on_non_3gpp_modem_has_no_imei_or_operator(fake_object):
    fake_object.modem_3gpp = None

    info = run(read_info(fake_object))

    assert info.imei is None
    assert info.operator_name is None
    assert info.operator_code is None


def test_empty_operator_name_becomes_none(fake_object):
    fake_object.modem_3gpp.operator_name = ""

    assert run(read_info(fake_object)).operator_name is None


def test_watch_calls_back_on_state_sim_network_and_signal_changes(fake_object):
    changes = []
    watch(fake_object, lambda: changes.append(1))

    for name in ("state", "signal-quality", "access-technologies", "sim"):
        fake_object.modem.emit(f"notify::{name}", None)
    for name in ("operator-name", "operator-code"):
        fake_object.modem_3gpp.emit(f"notify::{name}", None)

    assert len(changes) == 6


def test_watch_on_non_3gpp_modem_calls_back_on_modem_changes(fake_object):
    fake_object.modem_3gpp = None
    changes = []
    watch(fake_object, lambda: changes.append(1))

    fake_object.modem.emit("notify::state", None)

    assert changes == [1]


def test_unsubscribing_from_watch_stops_callbacks(fake_object):
    changes = []
    unsubscribe = watch(fake_object, lambda: changes.append(1))

    unsubscribe()
    fake_object.modem.emit("notify::signal-quality", None)

    assert changes == []
    assert fake_object.modem.handlers == {}
    assert fake_object.modem_3gpp.handlers == {}
    assert fake_object.handlers == {}


def test_watch_picks_up_3gpp_when_it_appears_after_unlock(fake_object):
    fake_object.modem_3gpp = None
    changes = []
    watch(fake_object, lambda: changes.append(1))

    fake_object.modem_3gpp = Fake3gppIface()
    fake_object.emit("interface-added", fake_object.modem_3gpp)
    fake_object.modem_3gpp.emit("notify::operator-name", None)
    fake_object.modem.emit("notify::state", None)

    assert len(changes) == 3


def test_watch_stops_watching_a_removed_interface(fake_object):
    removed = fake_object.modem_3gpp
    changes = []
    watch(fake_object, lambda: changes.append(1))

    fake_object.modem_3gpp = None
    fake_object.emit("interface-removed", removed)
    removed.emit("notify::operator-name", None)

    assert changes == [1]
    assert removed.handlers == {}


@pytest.mark.parametrize(
    ("iface", "names"),
    [
        (ModemManager.Modem, MODEM_PROPERTIES),
        (ModemManager.Modem3gpp, MODEM_3GPP_PROPERTIES),
    ],
    ids=["Modem", "Modem3gpp"],
)
def test_watched_names_are_real_properties(iface, names):
    assert [name for name in names if iface.find_property(name) is None] == []
