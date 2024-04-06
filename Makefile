PYTHON ?= python3
PIP ?= pip3


# Core paths
BUILD_PATH=$(PWD)/build
LOG_PATH=$(PWD)/logs
SOURCE_PATH=$(PWD)/src
PY_VENV=$(PWD)/venv

PB_PY_PATH=$(BUILD_PATH)/pb_types
PY_TYPES_PATH=$(BUILD_PATH)/py_types

PY_PATH=$(SOURCE_PATH):$(BUILD_PATH)

RUN_PY = PYTHONPATH=$(PY_PATH) $(PYTHON) -m
RUN_COVERAGE_PY = PYTHONPATH=$(PY_PATH) coverage run -m
BLACK_CMD = $(RUN_PY) black --line-length 100 .

# NOTE: exclude any virtual environment subdirectories here
PY_VENV_REL_PATH=$(subst $(PWD)/,,$(PY_VENV))
PY_BUILD_REL_PATH=$(subst $(PWD)/,,$(BUILD_PATH))
PY_FIND_COMMAND = find . -name '*.py' | grep -vE "($(PY_VENV_REL_PATH)|$(PY_BUILD_REL_PATH))"
MYPY_CONFIG=$(SOURCE_PATH)/mypy_config.ini

create_dirs:
	mkdir -p $(BUILD_PATH)
	mkdir -p $(LOG_PATH)

init: create_dirs
	@if [ -d "$(PY_VENV_REL_PATH)" ]; then \
		echo "\033[33mVirtual environment already exists\033[0m"; \
	else \
		$(PYTHON) -m venv $(PY_VENV_REL_PATH); \
	fi
	@echo "\033[0;32mRun 'source $(PY_VENV_REL_PATH)/bin/activate' to activate the virtual environment\033[0m"

install: types_clean
	$(PIP) install -r requirements.txt
	$(MAKE) types_build

format: isort
	$(BLACK_CMD)

check_format:
	$(BLACK_CMD) --check --diff

mypy:
	$(RUN_PY) mypy $(shell $(PY_FIND_COMMAND)) --config-file $(MYPY_CONFIG) --no-namespace-packages

pylint:
	$(RUN_PY) pylint $(shell $(PY_FIND_COMMAND))

autopep8:
	autopep8 --in-place --aggressive --aggressive $(shell $(PY_FIND_COMMAND))

isort:
	isort $(shell $(PY_FIND_COMMAND))

lint: check_format mypy pylint

test:
	$(RUN_COVERAGE_PY) unittest discover -s test -p *_test.py -v

clean: types_clean
	rm -rf $(PY_VENV)

### Scripts

.PHONY: init install format check_format mypy pylint autopep8 isort lint test clean
