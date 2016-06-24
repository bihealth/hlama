#!/usr/bin/env python3
"""Test for hlama pedigree app"""

import os.path
import pytest
from hlama import app

__author__ = 'Clemens Messerschmidt <clemens.messerschmidt@bihealth.de>'


@pytest.fixture
def report():
    """Report path"""
    return os.path.join(os.path.dirname(__file__),
                        'data/pedigree/report.txt')


@pytest.fixture
def tsv_file():
    """Path of tsv that describes donors and samples"""
    return os.path.join(os.path.dirname(__file__),
                        'data/pedigree/pedigree.ped.ext')


@pytest.fixture
def data_dir():
    """Path of sequencing data, i.e. fastq files"""
    return os.path.join(os.path.dirname(__file__),
                        'data/pedigree')


def test_app(tmpdir, report, tsv_file, data_dir):
    work_dir = str(tmpdir.mkdir('hlama_pedigree'))
    args = ['--pedigree', tsv_file, '--reads-base-dir', data_dir,
            '--work-dir', work_dir]
    app.main(args)

    with open(os.path.join(os.path.dirname(__file__), work_dir,
                           'report.txt')) as f:
        result = f.read().splitlines()
    with open(report, 'r') as f:
        solution = f.read().splitlines()

    assert set(result) == set(solution)

    with open(os.path.join(os.path.dirname(__file__), work_dir,
                           'daughter1.d/hla_types.txt')) as f:
        result = f.read().splitlines()
        assert result == ['A*01:01', 'A*02:01', 'B*07:02', 'B*08:01',
                          'C*01:06', 'C*02:02']

    with open(os.path.join(os.path.dirname(__file__), work_dir,
                           'father1.d/hla_types.txt')) as f:
        result = f.read().splitlines()
        assert result == ['A*01:03', 'A*02:01', 'B*07:02', 'B*07:05',
                          'C*01:06', 'C*02:02']

    with open(os.path.join(os.path.dirname(__file__), work_dir,
                           'mother1.d/hla_types.txt')) as f:
        result = f.read().splitlines()
        assert result == ['A*01:01', 'A*68:02', 'B*08:01', 'B*08:01',
                          'C*01:06', 'C*12:16']
