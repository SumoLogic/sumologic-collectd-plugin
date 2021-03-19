test: install pytest

install:
	python -m pip install -r requirements.txt

pytest:
	python -m pytest -v test/ --cov=sumologic_collectd_metrics/

pylint:
	python -m pylint **/*.py
