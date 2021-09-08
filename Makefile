test: install pytest

install:
	python -m pip install -r requirements.txt

pytest:
	python -m pytest -v test/ --cov=sumologic_collectd_metrics/

pylint:
	python -m pylint **/*.py

# https://packaging.python.org/tutorials/packaging-projects/
.PHONY: build
build:
	rm dist -r
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
