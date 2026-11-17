# SPDX-License-Identifier: GPL-3.0-or-later
import gi

# pygobject-stubs leaves out gi.version_info.
if gi.version_info < (3, 50):  # pyright: ignore[reportAttributeAccessIssue]
    raise ImportError(f"SIM Desk needs PyGObject 3.50 or newer, not {gi.__version__}")

gi.require_version("ModemManager", "1.0")
