UID=$(shell id -u)
DEBUG=debug

PYTHON=/usr/bin/python3
PIP := .virtualenv/bin/pip

all: help

help:
	@grep "##" Makefile | grep -v "@grep"

.virtualenv: ## Create Virtualenv
	virtualenv --no-site-packages -p ${PYTHON} .virtualenv
	${PIP} install -r requirements.txt

dev-tools: .virtualenv
	${PIP} install -r requirements-dev.txt

generate: .virtualenv
	.virtualenv/bin/python generate.py

clean: ## Clean some files
	@-rm -rf .virtualenv
