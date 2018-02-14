#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import, print_function

import io
import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()

print(find_packages('isanlp'))

setup(
    name='isanlp',
    version='0.0.1',
    description='ISA open-souce experimental library for natural language processing (NLP). Implements and wraps many linguistic parsers.',
    author='ISA RAS',
    author_email='',
    packages=['isanlp'] + ['isanlp.' + p for p in find_packages('isanlp')],
    #packages = ['isanlp'],
    #package_dir={'': 'isanlp'},
#    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
    ]
)

