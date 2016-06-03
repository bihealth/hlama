# -*- coding: utf-8 -*-
"""Main command line application for hlama"""

import argparse
import sys


def run(args):
    """Main entry point after parsing command line parameters"""


def main(argv=None):
    """Main entry point into the hlama application

    Parse command line and then call ``run()`` for the actual processing.
    """
    parser = argparse.ArgumentParser(
        description='HLA-typing based HTS sample matching')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--tumor-normal', type=argparse.FileType('rt'),
                       help=('Path to tumor/normal TSV file, '
                             'starts tumor/normal mode'))
    group.add_argument('--pedigree', type=argparse.FileType('rt'),
                       help=('Path to pedigree file, starts pedigree '
                             'mode'))

    parser.add_argument('--reads-base-dir', type=str, action='append',
                        default=[],
                        help=('Base directory for reads, give multiple '
                              'times for multiple places to search'))

    args = parser.parse_args(argv)
    return run(args)


if __name__ == '__main__':
    sys.exit(main())
