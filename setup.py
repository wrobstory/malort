# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='malort',
    version='0.0.1',
    description='JSON to Postgres Column Types',
    author='Rob Story',
    author_email='wrobstory@gmail.com',
    license='MIT License',
    url='https://github.com/wrobstory/malort',
    keywords='JSON Postgres postgres json',
    classifiers=['Development Status :: 4 - Beta',
                 'Programming Language :: Python :: 3.4.1',
                 'License :: OSI Approved :: MIT License'],
    packages=['malort']
)
