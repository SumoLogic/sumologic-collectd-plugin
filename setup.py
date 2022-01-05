from setuptools import setup


def readme():
    with open("README.rst") as f:
        return f.read()


setup(
    name="sumologic_collectd_metrics",
    version="4.1.0",
    description="A collectd output plugin to send Carbon 2.0-formatted metrics to Sumo Logic.",
    long_description=readme(),
    url="https://github.com/SumoLogic/sumologic-collectd-plugin",
    author="Sumo Logic",
    author_email="support@sumologic.com",
    license="Apache Software License, Version 2.0",
    packages=["sumologic_collectd_metrics"],
    install_requires=["requests", "retry"],
    tests_require=["pytest", "urllib3", "pytest-cov"],
    zip_safe=False,
)
