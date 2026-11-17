# SPDX-License-Identifier: GPL-3.0-or-later
from collections.abc import Callable

# pygobject-stubs has no ModemManager types.
from gi.repository import Gio, GLib, ModemManager  # pyright: ignore[reportAttributeAccessIssue]


class ModemManagerUnavailableError(RuntimeError):
    pass


class Manager:
    """Wraps a ModemManager.Manager. Each modem is a ModemManager.Object."""

    def __init__(self, mm_manager):
        self._mm = mm_manager

    @classmethod
    def connect(cls, connection: Gio.DBusConnection | None = None) -> "Manager":
        """Connects to ModemManager on the system bus, or on the given connection.

        Raises:
            ModemManagerUnavailableError: The bus can't be reached or the daemon
                is not running.
        """
        try:
            connection = connection or Gio.bus_get_sync(Gio.BusType.SYSTEM, None)
            mm_manager = ModemManager.Manager.new_sync(
                connection,
                Gio.DBusObjectManagerClientFlags.DO_NOT_AUTO_START,
                None,
            )
        except GLib.Error as err:
            raise ModemManagerUnavailableError(
                f"Can't connect to ModemManager: {err.message}"
            ) from err
        if mm_manager.get_name_owner() is None:
            raise ModemManagerUnavailableError("ModemManager is not running")
        return cls(mm_manager)

    def modems(self) -> list:
        return self._mm.get_objects()

    def on_modem_added(self, callback: Callable[[object], None]) -> int:
        return self._mm.connect("object-added", lambda _mgr, obj: callback(obj))

    def on_modem_removed(self, callback: Callable[[str], None]) -> int:
        return self._mm.connect(
            "object-removed", lambda _mgr, obj: callback(obj.get_object_path())
        )
