PYTHON ?= python3
PIP ?= pip3


# Core paths
LOG_PATH=$(PWD)/logs
SOURCE_PATH=$(PWD)/src
NOTEBOOK_PATH=$(PWD)/notebooks
PY_VENV=$(PWD)/venv

PY_PATH=$(SOURCE_PATH)

RUN_PY = PYTHONPATH=$(PY_PATH) $(PYTHON) -m
RUN_COVERAGE_PY = PYTHONPATH=$(PY_PATH) coverage run -m
BLACK_CMD = $(RUN_PY) black --line-length 100 .
NOTEBOOK_BLACK_CMD = $(RUN_PY) black --line-length 100 $(NOTEBOOK_PATH)/*

# NOTE: exclude any virtual environment subdirectories here
PY_VENV_REL_PATH=$(subst $(PWD)/,,$(PY_VENV))
PY_FIND_COMMAND = find . -name '*.py' | grep -vE "$(PY_VENV_REL_PATH)"
MYPY_CONFIG=$(SOURCE_PATH)/mypy_config.ini

create_dirs:
	mkdir -p $(LOG_PATH)

init: create_dirs
	@if [ -d "$(PY_VENV_REL_PATH)" ]; then \
		echo "\033[33mVirtual environment already exists\033[0m"; \
	else \
		$(PYTHON) -m venv $(PY_VENV_REL_PATH); \
	fi
	@echo "\033[0;32mRun 'source $(PY_VENV_REL_PATH)/bin/activate' to activate the virtual environment\033[0m"

install:
	$(PIP) install -r requirements.txt

format: isort
	$(BLACK_CMD)
	$(NOTEBOOK_BLACK_CMD)

check_format:
	$(BLACK_CMD) --check --diff
	$(NOTEBOOK_BLACK_CMD) --check --diff

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

notebook_clean:
	find . -name '*.ipynb' -exec nb-clean clean {} \;

upgrade: install
	pip install --upgrade $$(pip freeze | awk '{split($$0, a, "=="); print a[1]}')
	pip freeze > requirements.txt

clean:
	rm -rf $(PY_VENV)

### Scripts

.PHONY: init install format check_format mypy pylint autopep8 isort lint test notebook_clean upgrade clean
