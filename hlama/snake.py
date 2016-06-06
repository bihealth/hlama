# -*- coding: utf-8 -*-
"""Connection between snakemake and HLAMA"""

import fnmatch
import json
import os
import sys

from .base import HLAType
from .pedigree import Pedigree, PedigreeMember, check_consistency, \
    check_identity
from .app import PATTERNS_R1, PATTERNS_R2
from . import config

from hlama import __version__


class HlamaSchema:

    def __init__(self, data):
        self.data = data
        if self.data['version'] != __version__:
            raise Exception(('Incompatible data.json version, hlama '
                             'has version {}').format(__version__))
        self.load_config()

    def load_config(self):
        config_path = self.data['config']
        if config_path:
            if not os.path.exists(config_path):
                print('No configuration file at {}'.format(config_path),
                      file=sys.stderr)
                return 1
            self.conf = config.Configuration.load(config_path)
        elif os.path.exists(os.path.expanduser('~/.hlama.cfg')):
            self.conf = config.Configuration.load(
                os.path.expanduser('~/.hlama.cfg'))
        else:
            self.conf = config.Configuration.load(os.path.join(
                os.path.dirname(__file__), 'default_config.ini'))

    def command_prefix(self):
        return self.conf.cmd_prefix()

    def optitype_ini(self):
        return os.path.join(os.path.dirname(__file__), 'optitype.ini')

    def get_report_input(self):
        result = []
        for member in self.data['members'].values():
            tpl = '{}.d/hla_types.txt'
            yield tpl.format(member['name'])

    def get_hla_ref(self):
        return os.path.join(os.path.dirname(__file__),
                            'hla_reference_dna.fasta.gz')

    def get_first_read_paths(self, wildcards):
        member = self.data['members'][wildcards.sample]
        for path in member['files']:
            for pattern in PATTERNS_R1:
                if fnmatch.fnmatch(path, pattern):
                    yield path

    def get_second_read_paths(self, wildcards):
        member = self.data['members'][wildcards.sample]
        for path in member['files']:
            for pattern in PATTERNS_R2:
                if fnmatch.fnmatch(path, pattern):
                    yield path


    def _build_pedigree(self):
        members = []
        for member in self.data['members'].values():
            members.append(PedigreeMember(
                member['family'],
                member['name'],
                member['father'],
                member['mother'],
                member['gender'],
                member['disease']))
        return Pedigree(members)

    # TODO: refactor out of here, only applies to pedigree
    def check_consistency(self, out_path):
        pedigree = self._build_pedigree()

        print('Loading HLA calls...', file=sys.stderr)
        all_calls = {}
        calls = {}
        for member in pedigree.members:
            donor = member.name
            all_calls[donor] = []
            calls[donor] = {'A': [], 'B': [], 'C': []}
            with open('{}.d/hla_types.txt'.format(donor), 'rt') as fcalls:
                for hla_type in sorted(HLAType.parse(line.strip())
                                       for line in fcalls):
                    calls[donor][hla_type.gene_name].append(hla_type)
                    all_calls[donor].append(hla_type)

        print('Collecting index members...', file=sys.stderr)
        index_members = [member.name for member in pedigree.members
                         if member.father != '0' or member.mother != '0']

        print('Checking for consistency...', file=sys.stderr)
        with open(out_path, 'wt') as f:
            for index in index_members:
                # get IDs of parents
                index_member = pedigree.by_name[index]
                father = index_member.father
                mother = index_member.mother
                # check for identity to any parent, flag warning
                flags = []
                for digits in (2, 4):
                    if check_identity(digits, calls[index],
                                      calls.get(father)):
                        flags.append('WARN:identity-father:{}'.format(digits))
                    if check_identity(digits, calls[index],
                                      calls.get(mother)):
                        flags.append('WARN:identity-mother:{}'.format(digits))
                # check for 4 digit consistency
                mm4 = check_consistency(4, calls[index], calls.get(father),
                                        calls.get(mother))
                # check for 2 digit consistency
                mm2 = check_consistency(2, calls[index], calls.get(father),
                                        calls.get(mother))
                # get count of present parents
                num_parents = len({father, mother} - {'0'})
                # print result line
                print('\t'.join(map(str, [
                    index, num_parents, mm2 or 'OK', mm4 or 'OK',
                    ','.join(flags) or 'OK'
                ])), file=f)


def build_schema(path):
    with open(path, 'rt') as f:
        data = json.load(f)
    return HlamaSchema(data)
