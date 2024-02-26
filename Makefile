#########
# Tasks #
#########

# Setup the local development environment with python3 venv and project dependencies
#
#   make dev/setup
#
dev/setup:
	pyenv virtualenv -f $(PYTHON_VERSION) $(PROJECT_NAME)-$(PYTHON_VERSION)
	( \
		. $(PYTHON_BIN)/activate; \
		pip3 install -U pip setuptools; \
		pip3 install -r requirements.txt; \
		playwright install; \
		playwright install-deps; \
	)

dev/run: dev/setup dependencies/services
	( \
		. $(PYTHON_BIN)/activate; \
		ENVIRONMENT=LOCAL python3 -m src.restaurant_hub.app; \
	)
	( \
        . $(PYTHON_BIN)/activate; \
        ENVIRONMENT=LOCAL python3 -m src.restaurant_hub.app; \
    )

# Setup the circleci environment with project dependencies
#
#   make circleci/setup
#
circleci/setup:
	( \
		pip3 install -U pip setuptools; \
		pip3 install -r requirements.txt; \
		playwright install; \
		playwright install-deps; \
	)

# Run the pending migrations against the configured database (default to docker/local database)
#
#   make circleci/db/migrate
#
circleci/db/migrate:
	( \
		python --version; \
		alembic -x DB_URL=$(TEST_MIGRATE_DB_URL) upgrade head; \
	)

# Run tests in circleci
#
#   make circleci/test
#
circleci/test:
	py.test --cov=src/infrastructure --cov=src/restaurant_hub --cov=src/catalogs --cov=src/restaurants --cov-report=xml:coverage-reports/coverage.xml test -n 10 -p no:warnings --dist loadscope --max-worker-restart 0

# Run tests in local environment
#
#   make test
#
test: dependencies/services test/run dependencies/clean/services
test/run:
	( \
		. $(PYTHON_BIN)/activate; \
		py.test --cov=src/infrastructure --cov=src/restaurant_hub --cov=src/catalogs --cov=src/restaurants --cov-report=xml:coverage-reports/coverage.xml test -n 10 -p no:warnings --dist loadscope --max-worker-restart 0; \
	)

# Run playwright codegen
#
#   make playwright/codegen path=sign-in
#
playwright/codegen:
	( \
		. $(PYTHON_BIN)/activate; \
		playwright codegen http://127.0.0.1:5000/$(path); \
	)

# Generate a new migration file that holds a database change
#
#   make db/migration name=add_poc_table
#
db/migration:
	( \
		. $(PYTHON_BIN)/activate; \
		alembic revision -m $(name); \
	)

# Run the pending migrations against the configured database (default to docker/local database)
#
#   make db/migrate
#
db/migrate:
	( \
		. $(PYTHON_BIN)/activate; \
		alembic -x DB_URL=$(TEST_MIGRATE_DB_URL) upgrade head; \
	)

# Setup dependent services and third party dependencies
#
#   make dependencies/services
#
dependencies/services: dependencies/services/run db/migrate i18n/compile
dependencies/services/run:
	docker-compose up -d --wait
dependencies/clean/services:
	docker-compose stop && docker-compose rm -vf

# Setup i18n
#
#   make i18n/setup
#
i18n/setup:
	( \
		. $(PYTHON_BIN)/activate; \
		pybabel extract -F babel.cfg -k _l -o src/infrastructure/i18n/messages.pot .; \
		pybabel update -i src/infrastructure/i18n/messages.pot -d src/infrastructure/i18n; \
	)

# Generate a new language file
#
#   make i18n/language/add language=es
#
i18n/language/add:
	( \
		. $(PYTHON_BIN)/activate; \
		pybabel init -i src/infrastructure/i18n/messages.pot -d src/infrastructure/i18n -l $(language); \
	)

# Compile language files
#
#   make i18n/compile
#
i18n/compile: i18n/setup
	( \
		. $(PYTHON_BIN)/activate; \
		pybabel compile -d src/infrastructure/i18n; \
	)

# Download and package third party dependent libraries into project to be deployed
#
#   deploy/libs/package
#
deploy/libs/package:
	mkdir -p $(LAYERS_PATH)
	mkdir -p $(DEPENDENCY_LAYER_PATH)
	pip3 install -r requirements/prod.txt -t $(PYTHON_SITE_PACKAGES_PATH)
	rm -rf $(PYTHON_SITE_PACKAGES_PATH)/botocore*
	rm $(PYTHON_SITE_PACKAGES_PATH)/psycopg2/*.so
	cp _psycopg.cpython-39-x86_64-linux-gnu.so $(PYTHON_SITE_PACKAGES_PATH)/psycopg2/

# Build package, migrate database and deploy application to the given `stage`
#
#   make deploy stage=dev dryrun=true
#
deploy: deploy/libs/package deploy/migrate-db
	serverless deploy --stage $(stage)

deploy/migrate-db: deploy/db/migrate

deploy/db/migrate:
	alembic -x DB_URL=$(MIGRATE_DB_URL) upgrade head

# Prints the list of targets from this file
.PHONY: help test
help:
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'

###############
# Definitions #
###############

PROJECT_NAME ?= justeats
PYTHON ?= python
PYTHON_MAJOR_VERSION ?= 3.9
PYTHON_MINOR_VERSION ?= 9
PYTHON_VERSION ?= $(PYTHON_MAJOR_VERSION).$(PYTHON_MINOR_VERSION)
PYTHON_VENV ?= `pyenv root`/versions/$(PROJECT_NAME)-$(PYTHON_VERSION)
PYTHON_BIN ?= $(PYTHON_VENV)/bin

DB_USER ?= postgres
DB_PASSWORD ?= postgres
DB_HOST ?= localhost
DB_PORT ?= 5432
DB_NAME ?= justeats
MIGRATE_DB_URL := postgresql://$(DB_USER):$(DB_PASSWORD)@$(DB_HOST):$(DB_PORT)/$(DB_NAME)
TEST_MIGRATE_DB_URL := postgresql://postgres:postgres@localhost:5432/justeats

LAYERS_PATH := layers
DEPENDENCY_LAYER_PATH := $(LAYERS_PATH)/dependenciesLayer
PYTHON_DEPENDENCY_PATH := python/lib/python$(PYTHON_MAJOR_VERSION)/site-packages
PYTHON_SITE_PACKAGES_PATH := $(DEPENDENCY_LAYER_PATH)/$(PYTHON_DEPENDENCY_PATH)
