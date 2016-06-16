#!/usr/bin/env python3
"""Test for hlama tumor/normal app"""

import os.path
import pytest
from hlama import app

__author__ = 'Clemens Messerschmidt <clemens.messerschmidt@bihealth.de>'

@pytest.fixture
def report():
    """Report path"""
    return os.path.join(os.path.dirname(__file__),
                       'data/tumor_normal/report.txt')

@pytest.fixture
def tsv_file():
    """Path of tsv that describes donors and samples"""
    return os.path.join(os.path.dirname(__file__),
                       'data/tumor_normal/donors.tsv')

@pytest.fixture
def data_dir():
    """Path of sequencing data, i.e. fastq files"""
    return os.path.join(os.path.dirname(__file__),
                       'data/tumor_normal')

work_dir = 'hlama_test_tumor_normal'

def test_app(report, tsv_file, data_dir):
    args = ['--tumor-normal', tsv_file, '--reads-base-dir', data_dir,
            '--work-dir', work_dir]
    app.main(args)

    with open(os.path.join(os.path.dirname(__file__), work_dir,
        'report.txt')) as f:
        result = f.read().splitlines()
    with open(report, 'r') as f:
        solution = f.read().splitlines()

    assert set(result) == set(solution)
