# SIM Desk

SIM Desk lets you check and use the cellular modems on your Linux machine: see each modem's status and signal, send and read SMS, and run USSD codes. It's built on the [ModemManager](https://modemmanager.org/) D-Bus API.

## Requirements

- Linux with ModemManager running
- Python 3.12 or newer
- PyGObject (`python3-gi`, or [from pip](#installing-pygobject-with-pip-instead))
- ModemManager's GObject bindings (`gir1.2-modemmanager-1.0`)
- `make` and `git`

On Ubuntu 24.04 or newer, or Debian 13 or newer:

```bash
sudo apt install modemmanager python3-gi python3-venv gir1.2-modemmanager-1.0 make git
```

## Setup

```bash
git clone https://github.com/PromiseFru/sim-desk.git
cd sim-desk
make setup
```

`make setup` creates `venv` with the dev tools and installs the Git hooks. Each commit is checked for formatting, lint and types, and its message must follow [Conventional Commits](https://www.conventionalcommits.org/). Each push runs the tests. By default, the venv uses your distribution's PyGObject.

| Command | Does |
| --- | --- |
| `make run` | Print each modem's identity, state, network and signal |
| `make check` | Run the formatting, lint and type checks on all files |

> [!TIP]
> If `make run` prints `No modems found`, check that ModemManager sees your modem with `mmcli -L`.

### Installing PyGObject with pip instead

To build PyGObject from PyPI into the venv, for example with a Python other than the system one, install its build dependencies and pass `PYGOBJECT=pip`:

```bash
sudo apt install libgirepository-2.0-dev libcairo2-dev pkg-config python3-dev build-essential
make setup PYGOBJECT=pip
```

To use another Python, also pass `SYSTEM_PYTHON=/path/to/python3` to `make setup`. That Python needs its own development headers in place of `python3-dev`.

> [!IMPORTANT]
> The ModemManager bindings (`gir1.2-modemmanager-1.0`) aren't on PyPI. They describe the system's ModemManager library, so install them with apt either way.

> [!NOTE]
> To switch between the two setups, delete `venv` and run `make setup` again.

## License

SIM Desk is free software, licensed under the GNU General Public License v3.0 or later. See [LICENSE](LICENSE).
