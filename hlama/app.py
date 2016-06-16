# -*- coding: utf-8 -*-
"""Main command line application for hlama"""

import argparse
import fnmatch
import json
import os
import sys
import textwrap

from . import pedigree
from . import matched_pairs
from hlama import __version__

import snakemake


# ASCII art banner
BANNER = r"""
     _     _
    | |__ | | __ _ _ __ ___   __ _
    | '_ \| |/ _` | '_ ` _ \ / _` |
    | | | | | (_| | | | | | | (_| |
    |_| |_|_|\__,_|_| |_| |_|\__,_|
"""

# Single-end mode
SINGLE_END = 'single-end'
# Paired-end mode
PAIRED_END = 'paired-end'

# Patterns for first read
PATTERNS_R1 = [
    '*_1*.fastq.gz', '*_1*.fq.gz', '*_R1_*.fq.gz', '*_R1_*.fastq.gz',
    '*_R1.fastq.gz',
    '*_1*.fastq', '*_1*.fq', '*_R1_*.fq', '*_R1_*.fastq',
]
# Patterns for second read
PATTERNS_R2 = [
    '*_2*.fastq.gz', '*_2*.fq.gz', '*_R2_*.fq.gz', '*_R2_*.fastq.gz',
    '*_R2.fastq.gz',
    '*_2*.fastq', '*_2*.fq', '*_R2_*.fq', '*_R2_*.fastq',
]


class InputDataException(Exception):
    """Raised on problems with input data"""


class BaseApp:
    """Base class for the application

    There are two major modes: comparing matched tumor/normal samples and
    checking of samples from donors in a pedigree.  There is a BaseApp sub
    class for each.

    Uses the template class pattern, sub clases reimplement the relevant
    pieces.
    """

    def __init__(self, args):
        #: Command line arguments
        self.args = args

    def run(self):
        """Perform the checking"""
        print(BANNER + '\n', file=sys.stderr)
        # Create output directory and load information
        self.create_out_dir()
        self.info = self.load_info()
        # Check input data
        if self.args.perform_checks:
            self.check_info(self.info)
        # Create Snakefile
        with open(os.path.join(self.args.work_dir, 'data.json'), 'wt') as f:
            self.create_data_json(f, self.info)
        self.create_snakefile_link()
        # Stop here if we are not to run Snakemake or run it and display
        # where the result file is afterwards.
        if self.args.run_snakemake:
            self.run_snakemake()
        else:
            self.dont_run_snakemake()

    def create_snakefile_link(self):
        if not os.path.exists(os.path.join(self.args.work_dir, 'Snakefile')):
            os.symlink(os.path.join(os.path.dirname(__file__), 'Snakefile'),
                       os.path.join(self.args.work_dir, 'Snakefile'))

    def run_snakemake(self):
        """Run Snakemake and display result files afterwards"""
        print('\nRunning Snakemake\n=================\n', file=sys.stderr)
        snakemake.snakemake(
            snakefile=os.path.join(self.args.work_dir, 'Snakefile'),
            workdir=self.args.work_dir,
        )
        # TODO: check Snakemake result

        print('\nThe End\n=======\n', file=sys.stderr)
        print('\n'.join(textwrap.wrap(textwrap.dedent(r"""
            You can find the results in the "{}/report.txt" file.
            """).format(self.args.work_dir).lstrip())), file=sys.stderr)

    def dont_run_snakemake(self):
        """Don't run Snakemake and only display what to do afterwards"""
        print('\nThe End\n=======\n', file=sys.stderr)
        print('\n'.join(textwrap.wrap(textwrap.dedent(r"""
            Created Snakemake in "{}" but running it is disabled.  The next
            step is to change into this directory and call "snakemake".  Note
            that you can use Snakemake to run multi-threaded and even in a
            cluster environment.

            After running Snakemake, you will find the results in the
            "report.txt" file.
            """.format(self.args.work_dir)).lstrip(), 78)), file=sys.stderr)

    def create_out_dir(self):
        """Create output directory if it does not exist"""
        if not os.path.exists(self.args.work_dir):
            print('Creating {}...'.format(self.args.work_dir),
                  file=sys.stderr)
            os.makedirs(self.args.work_dir, exist_ok=True)
        else:
            print('Output directory {} already exists.'.format(
                self.args.work_dir), file=sys.stderr)

    def load_info(self):
        """Load pedigree/matched sample file"""
        raise NotImplementedError('Override me!')

    def check_info(self, info):
        """Check previously loaded info

        In particular, this is the right place to check for file paths,
        single-end, and paired and mode.
        """
        raise NotImplementedError('Override me!')

    def create_data_json(self, file, info):
        """Write out Snakefile"""
        raise NotImplementedError('Override me!')

    def get_mode(self, paths):
        """Return ``SINGLE_END`` or ``PAIRED_END`` from list of file paths

        Raise InputDataException if non-existing.
        """
        seen = {0: 0, 1: 0}  # counters
        for path in paths:
            filename = os.path.basename(path)
            for i, patterns in enumerate([PATTERNS_R1, PATTERNS_R2]):
                for pattern in patterns:
                    if fnmatch.fnmatch(filename, pattern):
                        seen[i] += 1
                        break
        if not seen[0] and seen[1]:
            raise InvalidDataException('Have seen only R2 in {}!'.format(
                ','.join(paths)))
        if seen[1] and seen[0] != seen[1]:
            raise InvalidDataException(
                'Have seen different number of R1 and R2 reads in {}'.format(
                ','.join(paths)))
        return (PAIRED_END if seen[1] else SINGLE_END)

    def locate_file(self, path):
        """Return full path to file at given path

        Will interpret ``self.args.reads_base_dirs``.
        """
        if path.startswith('/'):
            if not os.path.exists(path):
                tpl = 'Missing file at absolute path {}'
                raise InputDataException(tpl.format(path))
            else:
                return path
        else:
            for base_dir in self.args.reads_base_dirs or ['.']:
                full_path = os.path.join(base_dir, path)
                if os.path.exists(full_path):
                    return full_path
            else:
                tpl = 'Missing file at relative path {}'
                raise InputDataException(tpl.format(path))


class SomaticApp(BaseApp):
    """Application for the case of matched somatic samples"""

    def load_info(self):
        """Load config tsv and return it"""
        print('Loading tumor/normal pairs from {}...'.format(
            self.args.tumor_normal.name), file=sys.stderr)
        result = matched_pairs.Cohort.parse(self.args.tumor_normal)
        print('>>> pairs <<<', file=sys.stderr)
        result.print(sys.stderr)
        print('>>> /pairs <<<', file=sys.stderr)
        return result

    def check_info(self, config):
        """Check files for existence"""
        for member in config.members:
            paths = member.data[0].split(',')
            if not paths:
                tpl = 'Individual {} has no FASTQ files!'
                raise InputDataException(tpl.format(member.name))
            # Check that all files exist
            resolved = []
            for path in paths:
                try:
                    resolved.append(self.locate_file(path))
                except InputDataException as e:
                    tpl = 'Individual {} refers to non-existing path {}!'
                    raise InputDataException(tpl.format(
                        member.name, path))
            # Determine single-end or paired-end mode
            self.get_mode(resolved)

    def create_data_json(self, file, config):
        """Create ``data.json``"""
        result = {'schema': 'hla_check_pairs', 'members': {}}
        for member in config.members:
            paths = member.data[0].split(',')
            result['members'][member.name] = {
                'donor': member.donor,
                'sample': member.sample,
                'name': member.sample,
                'seq_type': member.seq_type,
                'reference': member.reference_sample,
                'files': list(map(self.locate_file, paths)),
                'mode': self.get_mode(paths),
            }
        result['config'] = self.args.config
        result['version'] = __version__
        result['num_threads'] = self.args.num_threads
        json.dump(result, file, sort_keys = True, indent=4)


class PedigreeApp(BaseApp):
    """Application for the case of samples from a pedigree"""

    def load_info(self):
        """Load pedigree and return it"""
        print('Loading pedigree from {}...'.format(
            self.args.pedigree.name), file=sys.stderr)
        result = pedigree.Pedigree.parse(self.args.pedigree)
        print('>>> pedigree <<<', file=sys.stderr)
        result.print(sys.stderr)
        print('>>> /pedigree <<<', file=sys.stderr)
        return result

    def check_info(self, pedigree):
        """Check files for existence"""
        for member in pedigree.members:
            paths = member.data[0].split(',')
            if not paths:
                tpl = 'Individual {} has no FASTQ files!'
                raise InputDataException(tpl.format(member.name))
            # Check that all files exist
            resolved = []
            for path in paths:
                try:
                    resolved.append(self.locate_file(path))
                except InputDataException as e:
                    tpl = 'Individual {} refers to non-existing path {}!'
                    raise InputDataException(tpl.format(
                        member.name, path))
            # Determine single-end or paired-end mode
            self.get_mode(resolved)

    def create_data_json(self, file, pedigree):
        """Create ``data.json``"""
        result = {'schema': 'hla_pedigree', 'members': {}}
        for member in pedigree.members:
            paths = member.data[0].split(',')
            result['members'][member.name] = {
                'family': member.family,
                'name': member.name,
                'father': member.father,
                'mother': member.mother,
                'gender': member.gender,
                'disease': member.disease,
                'files': list(map(self.locate_file, paths)),
                'mode': self.get_mode(paths),
            }
        result['config'] = self.args.config
        result['version'] = __version__
        result['num_threads'] = self.args.num_threads
        json.dump(result, file, sort_keys = True, indent=4)


def run(args):
    """Main entry point after parsing command line parameters"""
    try:
        if args.tumor_normal:
            return SomaticApp(args).run()
        else:
            return PedigreeApp(args).run()
    except InputDataException as e:
        print('ERROR: {}'.format(e), file=sys.stderr)
        return 1


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

    parser.add_argument('--config', type=str,
                        help=('Optional explicit path to configuration '
                              'file, by default ~/.hlama.cfg is searched '
                              'for'))

    parser.add_argument('--work-dir', type=str, default='hlama_work',
                        help='Directory to create the Snakefile in')
    parser.add_argument('--reads-base-dir', type=str, action='append',
                        dest='reads_base_dirs', default=[],
                        help=('Base directory for reads, give multiple '
                              'times for multiple places to search'))

    parser.add_argument('--dont-run-snakemake', dest='run_snakemake',
                        default=True, action='store_false',
                        help=('Only create Snakefile but do not run '
                              'Snakemake yet'))

    parser.add_argument('--disable-checks', dest='perform_checks',
                        default=True, action='store_false',
                        help='Disable input checks')

    parser.add_argument('--num-threads', default=8,
                        help=('Number of threads to use for read mapping, '
                              ' defaults to 8'))

    args = parser.parse_args(argv)
    return run(args)


if __name__ == '__main__':
    sys.exit(main())
