# SPDX-License-Identifier: GPL-3.0-or-later
import sys
from dataclasses import asdict

from simdesk.core.loop import run
from simdesk.core.manager import Manager, ModemManagerUnavailableError
from simdesk.core.modem import read_info


async def main() -> int:
    try:
        manager = await Manager.connect()
    except ModemManagerUnavailableError as err:
        print(err, file=sys.stderr)
        return 1

    modems = manager.modems()
    if not modems:
        print("No modems found")
    for mm_object in modems:
        for key, value in asdict(await read_info(mm_object)).items():
            print(f"{key:>20}: {value}")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(run(main()))
