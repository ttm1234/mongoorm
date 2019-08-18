#!/usr/bin/env python3
from setuptools import setup

setup(
    name='mongoorm',
    version='1.0.1.dev4',
    description='A mongodb orm python3 project',
    url='https://github.com/ttm1234/mongoorm',
    author='ttm1234',
    author_email='',
    license='Anti 996',
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='mongodb orm python python3',
    packages=[
        'mongoorm', 'mongoorm.doc_model', 'mongoorm.exceptions',
        'mongoorm.extensions', 'mongoorm.fields',
    ],
    install_requires=["pymongo>=3.7", "six", ],
    include_package_data=True,
)
