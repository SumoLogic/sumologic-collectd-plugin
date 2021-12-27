test: install pytest

install: install-lint install-test

install-test:
	python -m pip install -r requirements-test.txt

install-lint:
	python -m pip install -r requirements-lint.txt

pytest:
	python -m pytest -v test/ --cov=sumologic_collectd_metrics/

lint:
	python -m pylint **/*.py
	black --check .
	isort --check .

format:
	black .
	isort .

# https://packaging.python.org/tutorials/packaging-projects/
.PHONY: build
build:
	rm dist -rf
	python -m pip install virtualenv
	python -m pip install --upgrade build
	python -m build

.PHONY: push-test
push-test:
	python -m pip install --upgrade twine
	python -m twine upload --repository testpypi dist/*

.PHONY: push
push:
	python -m pip install --upgrade twine
	python -m twine upload dist/*
