# SPDX-License-Identifier: GPL-3.0-or-later
from collections.abc import Callable
from dataclasses import dataclass

# pygobject-stubs has no ModemManager types.
from gi.repository import GLib, ModemManager  # pyright: ignore[reportAttributeAccessIssue]

from simdesk.core.events import Unsubscribe, subscribe

MODEM_PROPERTIES = ("state", "signal-quality", "access-technologies", "sim")
MODEM_3GPP_PROPERTIES = ("operator-name", "operator-code")


@dataclass(frozen=True)
class ModemInfo:
    path: str
    manufacturer: str
    model: str
    revision: str
    imei: str | None
    imsi: str | None
    state: str
    operator_name: str | None
    operator_code: str | None
    access_technologies: str
    signal_quality: int
    signal_recent: bool


async def read_info(mm_object) -> ModemInfo:
    """Reads the identity, network and signal of a modem.

    IMEI and operator are None on a modem without 3GPP, such as a CDMA-only one.
    IMSI is None when no SIM is inserted or the SIM can't be read. Any of the three
    is None when the modem reports it empty (e.g. no operator before registering).
    """
    modem = mm_object.get_modem()
    modem_3gpp = mm_object.get_modem_3gpp()
    quality, recent = modem.get_signal_quality()
    technologies = modem.get_access_technologies()

    return ModemInfo(
        path=mm_object.get_object_path(),
        manufacturer=modem.get_manufacturer() or "",
        model=modem.get_model() or "",
        revision=modem.get_revision() or "",
        imei=_or_none(modem_3gpp and modem_3gpp.get_imei()),
        imsi=await _read_imsi(modem),
        state=ModemManager.modem_state_get_string(modem.get_state()),
        operator_name=_or_none(modem_3gpp and modem_3gpp.get_operator_name()),
        operator_code=_or_none(modem_3gpp and modem_3gpp.get_operator_code()),
        access_technologies=(
            ModemManager.modem_access_technology_build_string_from_mask(technologies)
        ),
        signal_quality=quality,
        signal_recent=recent,
    )


async def _read_imsi(modem) -> str | None:
    if modem.dup_sim_path() in {None, "", "/"}:
        return None
    try:
        sim = await modem.get_sim()
    except GLib.Error:
        return None
    return _or_none(sim and sim.get_imsi())


def watch(mm_object, callback: Callable[[], None]) -> Unsubscribe:
    """Calls callback whenever the modem's state, SIM, network or signal changes.

    Also calls it when ModemManager adds or removes one of the modem's interfaces,
    such as 3GPP once a locked SIM is unlocked, and watches the new one.
    """
    watched = []  # (interface, its unsubscribe functions)

    def watch_current_interfaces():
        for iface, names in (
            (mm_object.get_modem(), MODEM_PROPERTIES),
            (mm_object.get_modem_3gpp(), MODEM_3GPP_PROPERTIES),
        ):
            if iface is not None and not any(iface is w for w, _ in watched):
                notify = [
                    subscribe(iface, f"notify::{name}", lambda *_: callback())
                    for name in names
                ]
                watched.append((iface, notify))

    def drop(entries):
        for entry in entries:
            for unsubscribe_one in entry[1]:
                unsubscribe_one()
            watched.remove(entry)

    def on_interfaces_changed(*_):
        current = (mm_object.get_modem(), mm_object.get_modem_3gpp())
        drop([e for e in watched if not any(e[0] is iface for iface in current)])
        watch_current_interfaces()
        callback()

    watch_current_interfaces()
    object_subscriptions = [
        subscribe(mm_object, "interface-added", on_interfaces_changed),
        subscribe(mm_object, "interface-removed", on_interfaces_changed),
    ]

    def unsubscribe():
        for unsubscribe_one in object_subscriptions:
            unsubscribe_one()
        drop(list(watched))

    return unsubscribe


def _or_none(value: str | None) -> str | None:
    return value or None
