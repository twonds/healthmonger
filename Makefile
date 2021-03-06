APP_DIR := $(patsubst %/,%,$(dir $(realpath $(lastword $(MAKEFILE_LIST)))))
VENV ?= .venv

.PHONY: all check clean venv update-venv clean-venv clean-pyc

all: check
build: all
test: check

venv: $(VENV)/installed

$(VENV)/installed:
	mkdir -p $(APP_DIR)/data
	mkdir -p $(APP_DIR)/index
	type -p virtualenv || sudo pip install virtualenv
	test -d $(VENV) || virtualenv $(VENV)
	$(VENV)/bin/python $(VENV)/bin/pip install -r requirements.txt
	touch $(VENV)/installed

update-venv:
	$(VENV)/bin/python $(VENV)/bin/pip install -Ur requirements.txt

clean-venv:
	@ [ ! -w "$(VENV)" ] || rm -rf $(VENV)

clean-pyc:
	find $(APP_DIR) -name "*.pyc" -delete

clean-emacs:
	find $(APP_DIR) -name "*~" -delete

clean-logs:
	$(RM) $(APP_DIR)/logs/*.log

clean-data:
	$(RM) -rf $(APP_DIR)/data/*

clean-index:
	$(RM) -rf $(APP_DIR)/index/*

clean: clean-venv clean-pyc clean-emacs clean-logs clean-reports

flake-check:
	$(VENV)/bin/flake8 $(APP_DIR)/tests $(APP_DIR)/healthmonger

check-unit: venv flake-check
	$(VENV)/bin/nosetests $(APP_DIR)/tests


start: venv
	mkdir -p $(APP_DIR)/logs
	$(VENV)/bin/python $(APP_DIR)/healthmonger/healthmonger.py >> $(APP_DIR)/logs/healthmonger.log 2>> $(APP_DIR)/logs/errors.log &

stop:
	ps -ef | awk "/python/ && !/grep/ && /healthmonger.py/ {print "'$$2'"}" | xargs kill -KILL || echo 'nothing to kill'


status:
	@echo ""
	curl "http://localhost:5000/status"
	@echo "\n"

api-example:
	@echo ""
	curl "http://localhost:5000/"
	@echo "\n"

TAGS ?= -skip

STEPS := $(wildcard integration/features/steps/*.py)
FEATURES := $(wildcard integration/features/*.feature)
FEATURE_REPORTS := $(FEATURES:integration/features/%.feature=integration/reports/%.feature.report)

ALL_TGTS += $(FEATURE_REPORTS)

$(FEATURE_REPORTS) : integration/reports/%.feature.report : integration/features/%.feature $(STEPS)
	mkdir -p $(dir $@)
	$(RM) -f $@
	$(VENV)/bin/behave $(VERBOSE:%=--verbose) $(TAGS:%=--tags=%) $<

.PHONY: clean-reports
clean-reports:
	$(RM) $(FEATURE_REPORTS)

check-integration: clean-reports $(FEATURE_REPORTS)

check: clean check-unit start check-integration stop

travis:
	flake8 tests healthmonger
	nosetests tests
	mkdir -p logs
	python healthmonger/healthmonger.py >> logs/healthmonger.log 2>> logs/errors.log &
	behave integration/features/healthmonger.feature
