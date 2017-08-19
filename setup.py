from setuptools import setup

setup(name='sumologic_collectd_plugin',
      version='1.0.0',
      description='A collectd output plugin to send Carbon 2.0-formatted metrics to Sumo Logic.',
      url='https://github.com/SumoLogic/sumologic-collectd-plugin',
      author='Sumo Logic',
      author_email='support@sumologic.com',
      license='Apache Software License, Version 2.0',
      packages=['sumologic_collectd_plugin'],
      zip_safe=False)