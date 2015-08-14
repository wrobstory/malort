# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

reqs = ["dask>=0.7.0",
        "dill>=0.2.4",
        "numpy>=1.9.2",
        "pandas>=0.16.2",
        "python-dateutil>=2.4.2",
        "pytz>=2015.4",
        "six>=1.9.0",
        "toolz>=0.7.2",
        "wheel>=0.24.0"]


setup(
    name='malort',
    version='0.0.4',
    description='JSON to Postgres Column Types',
    author='Rob Story',
    author_email='wrobstory@gmail.com',
    license='MIT License',
    url='https://github.com/wrobstory/malort',
    keywords='JSON Postgres postgres json',
    classifiers=['Development Status :: 4 - Beta',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 3',
                 'License :: OSI Approved :: MIT License'],
    packages=['malort'],
    install_requires=reqs
)
