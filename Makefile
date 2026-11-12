PYTHON ?= python3
VENV ?= .venv
BIN := $(VENV)/bin
PIP := $(BIN)/pip
PY := $(BIN)/python
APP := install_nerd_fonts.py
DESTINATION ?= fonts
INCLUDE ?=
EXCLUDE ?=

.PHONY: help venv install install-dev list show menu download download-all tui test clean clean-downloads

help:
	@echo "Targets:"
	@echo "  make venv             Create the virtual environment"
	@echo "  make install          Install runtime dependencies"
	@echo "  make install-dev      Install runtime and dev dependencies"
	@echo "  make list             List available fonts"
	@echo "  make show INCLUDE=Fira"
	@echo "  make menu             Open the Fire CLI menu"
	@echo "  make download INCLUDE=Fira [EXCLUDE=Propo] [DESTINATION=fonts]"
	@echo "  make download-all [EXCLUDE=Propo] [DESTINATION=fonts]"
	@echo "  make tui              Open the Textual menu"
	@echo "  make test             Run pytest"
	@echo "  make clean            Remove Python caches"
	@echo "  make clean-downloads  Remove downloaded zip files"

venv:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip

install: venv
	$(PIP) install -r requirements.txt

install-dev: install
	@if [ -f requirements-dev.txt ]; then \
		$(PIP) install -r requirements-dev.txt; \
	else \
		$(PIP) install pytest; \
	fi

list: install
	$(PY) $(APP) list

show: install
	@if [ -z "$(INCLUDE)" ]; then \
		echo "Usage: make show INCLUDE=Fira"; \
		exit 1; \
	fi
	$(PY) $(APP) show "$(INCLUDE)"

menu: install
	$(PY) $(APP) menu --destination "$(DESTINATION)" --include "$(INCLUDE)" --exclude "$(EXCLUDE)"

download: install
	@if [ -z "$(INCLUDE)" ]; then \
		echo "Usage: make download INCLUDE=Fira [EXCLUDE=Propo] [DESTINATION=fonts]"; \
		exit 1; \
	fi
	$(PY) $(APP) download "$(INCLUDE)" --exclude "$(EXCLUDE)" --destination "$(DESTINATION)"

download-all: install
	$(PY) $(APP) download_all --exclude "$(EXCLUDE)" --destination "$(DESTINATION)"

tui: install
	$(PY) $(APP) tui --destination "$(DESTINATION)" --include "$(INCLUDE)" --exclude "$(EXCLUDE)"

test: install-dev
	$(PY) -m pytest

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +

clean-downloads:
	find . -maxdepth 2 -type f -name "*.zip" -delete
