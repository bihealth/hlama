#!/usr/bin/env python3
import sys

from setuptools import setup, find_packages

from hlama import __version__

setup(
    name='hlama',
    version=__version__,
    description='HLA-typing based HTS sample matching',
    license='MIT',
    author='Manuel Holtgrewe, Clemens Messerschmidt',
    author_email='manuel.holtgrewe@bihealth.de, clemens.messerschmit@bihealth.de',
    url='https://github.com/bihealth/hlama',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'hlama = hlama.app:main',
        ],
    },
    install-requires=[
        'snakemake>=3.7.1',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Bio-Informatics'
    ],
    zip_safe=False,
)
