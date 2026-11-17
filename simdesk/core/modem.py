# SPDX-License-Identifier: GPL-3.0-or-later
from dataclasses import dataclass

# pygobject-stubs has no ModemManager types.
from gi.repository import GLib, ModemManager  # pyright: ignore[reportAttributeAccessIssue]


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


def read_info(mm_object) -> ModemInfo:
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
        imsi=_read_imsi(modem),
        state=ModemManager.modem_state_get_string(modem.get_state()),
        operator_name=_or_none(modem_3gpp and modem_3gpp.get_operator_name()),
        operator_code=_or_none(modem_3gpp and modem_3gpp.get_operator_code()),
        access_technologies=(
            ModemManager.modem_access_technology_build_string_from_mask(technologies)
        ),
        signal_quality=quality,
        signal_recent=recent,
    )


def _read_imsi(modem) -> str | None:
    if modem.dup_sim_path() in {None, "", "/"}:
        return None
    try:
        sim = modem.get_sim_sync(None)
    except GLib.Error:
        return None
    return _or_none(sim and sim.get_imsi())


def _or_none(value: str | None) -> str | None:
    return value or None
