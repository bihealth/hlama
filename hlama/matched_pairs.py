# -*- coding: utf-8 -*-
"""Implementation of the pedigree checking"""

from . import base
from collections import Counter


class Donor:
    """Representation of one Donor line"""

    @classmethod
    def parse_line(klass, line):
        arr = line.strip().split()
        return Donor(*arr[0:4], data=arr[4:])

    def __init__(self, donor, sample, reference_sample,
                 seq_type, data=[]):
        self.donor = donor
        self.sample = sample
        self.name = sample
        self.reference_sample = reference_sample
        self.seq_type = seq_type
        self.data = list(data)

    def __str__(self):
        return 'Donor({})'.format(', '.join(map(str, [
            self.donor,
            self.sample,
            self.reference_sample,
            self.seq_type,
            ])))

    def print(self, file):
        print('\t'.join([
            self.donor,
            self.sample,
            self.reference_sample,
            self.seq_type,
            ]),
              file=file)


class Cohort:
    """Representation of a cohort"""

    @classmethod
    def parse(klass, f):
        """Parse from file-like object"""
        members = []
        for line in f:
            line = line.strip()
            if not line:
                continue  # skip empty lines
            members.append(Donor.parse_line(line))
        return Cohort(members)

    def __init__(self, members=[]):
        self.members = list(members)
        self.by_name = {m.name: m for m in self.members}

    def print(self, file):
        """Print pedigree to the given file"""
        for member in self.members:
            member.print(file)


def check_consistency(precision, normal_calls, tumor_calls):
    """Check for consistency precision is given by precision

    Return number of mismatches
    """

    def to_str(hla):
        return hla.prec_str(precision)

    ref = Counter(normal_calls)
    sample = Counter(tumor_calls)
    mismatches = len(list((ref - sample).elements()))
    return mismatches
