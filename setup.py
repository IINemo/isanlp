#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import, print_function

import io
from os.path import dirname
from os.path import join

from setuptools import setup


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


setup(
    name='isanlp',
    version='0.0.7',
    description='ISA open-souce experimental library for natural language processing (NLP). Implements and wraps many linguistic parsers.',
    author='ISA RAS',
    author_email='',
    packages=['isanlp', 'isanlp.ru', 'isanlp.en', 'isanlp.utils'],
    include_package_data=True,
    zip_safe=False,
    package_dir={'': 'src'},
    install_requires=['protobuf==3.18.3', 'grpcio']
)
