# SPDX-License-Identifier: GPL-3.0-or-later

# With PYGOBJECT=system, this Python must have the distribution's PyGObject
# (python3-gi) installed.
SYSTEM_PYTHON ?= /usr/bin/python3
PYTHON ?= venv/bin/python
PYGOBJECT ?= system

ifeq ($(filter $(PYGOBJECT),system pip),)
$(error PYGOBJECT must be system or pip, not "$(PYGOBJECT)")
endif

ifeq ($(PYGOBJECT),system)
VENV_FLAGS := --system-site-packages
endif

.PHONY: setup run test coverage check clean

setup: venv/bin/python
	$(PYTHON) -m pip install -r requirements-dev.txt
ifeq ($(PYGOBJECT),pip)
	$(PYTHON) -m pip install -r requirements-pygobject.txt
endif
	$(PYTHON) -m pre_commit install --install-hooks

venv/bin/python:
	$(SYSTEM_PYTHON) -m venv $(VENV_FLAGS) venv

run:
	$(PYTHON) -m simdesk.core

test:
	$(PYTHON) -m pytest $(PYTEST_ARGS)

coverage:
	$(PYTHON) -m pytest --cov $(PYTEST_ARGS)

check:
	$(PYTHON) -m pre_commit run --all-files

clean:
	rm -rf .pytest_cache .ruff_cache .coverage
