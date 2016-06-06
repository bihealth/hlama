# -*- coding: utf-8 -*-
"""Implementation of the pedigree checking"""

from . import base


class PedigreeMember:
    """Representation of one PED file line"""

    UNKNOWN = '0'
    MALE = '1'
    FEMALE = '2'
    UNAFFECTED = '1'
    AFFECTED = '2'

    @classmethod
    def parse_line(klass, line):
        arr = line.strip().split()
        return PedigreeMember(*arr[0:6], data=arr[6:])

    def __init__(self, family, name, father, mother, gender, disease,
                 data=[]):
        self.family = family
        self.name = name
        self.father = father
        self.mother = mother
        self.gender = gender
        self.disease = disease
        self.data = list(data)

    def __str__(self):
        return 'PedigreeMember({})'.format(', '.join(map(str, [
            self.family, self.name, self.father, self.mother, self.gender,
            self.disease])))

    def print(self, file):
        print('\t'.join([self.family, self.name, self.father, self.mother,
                         self.gender, self.disease]),
              file=file)


class Pedigree:
    """Representation of a pedigree"""

    @classmethod
    def parse(klass, f):
        """Parse from file-like object"""
        members = []
        for line in f:
            line = line.strip()
            if not line:
                continue  # skip empty lines
            members.append(PedigreeMember.parse_line(line))
        return Pedigree(members)

    def __init__(self, members=[]):
        self.members = list(members)
        self.by_name = {m.name: m for m in self.members}

    def print(self, file):
        """Print pedigree to the given file"""
        for member in self.members:
            member.print(file)


def check_consistency(precision, index_calls, father_calls, mother_calls):
    """Check for consistency precision is given by precision

    Return number of mismatches
    """

    def to_str(hla):
        return hla.prec_str(precision)

    mismatches = 0
    for gene in 'ABC':
        summand = 0
        index_set = set(map(to_str, index_calls[gene]))
        father_set = set(map(to_str, father_calls[gene]))
        mother_set = set(map(to_str, mother_calls[gene]))
        if father_calls and mother_calls:
            # have both mother and father calls, more complex
            # print('index', index_set, 'father', father_set, 'mother',
            #       mother_set)
            if not index_set & father_set:
                summand = 1
            if not index_set & mother_set:
                summand = max(summand, 1)
            if len(index_set) == 1:
                if not index_set & father_set or not index_set & mother_set:
                    summand = 2
            else:
                summand = 2 - len(index_set & (mother_set | father_set))
            # print('gene {} summand {}'.format(gene, summand),
            #       file=sys.stdout)
        else:
            # have only one calls, easier
            either_set = father_set or mother_set
            if not either_set & index_set:
                summand = 1
        mismatches += summand
    return mismatches


def check_identity(precision, lhs_calls, rhs_calls):
    """Check for identity up to the given precision"""

    def to_str(hla):
        return hla.prec_str(precision)

    for gene in 'ABC':
        lhs_set = set(map(to_str, lhs_calls[gene]))
        rhs_set = set(map(to_str, rhs_calls[gene]))
        if lhs_set != rhs_set:
            return False
    return True


def run(args):
    """Run the consistency check"""
    # Load the pedigree file
    print('Parsing pedigree...', file=sys.stderr)
    pedigree = Pedigree.parse(args.input_ped)
    for member in pedigree.members:
        print(member, file=sys.stderr)
    # load the HLA calls for each donor
    print('Loading HLA calls...', file=sys.stderr)
    all_calls = {}
    calls = {}
    for donor, fcalls in zip(args.donor_name, args.donor_calls):
        print(donor, fcalls.name, file=sys.stderr)
        all_calls[donor] = []
        calls[donor] = {'A': [], 'B': [], 'C': []}
        for hla_type in sorted(HLAType.parse(line.strip())
                               for line in fcalls):
            calls[donor][hla_type.gene_name].append(hla_type)
            all_calls[donor].append(hla_type)
    print('Checking for consistency...', file=sys.stderr)
    # get IDs of parents
    index_member = pedigree.by_name[args.index_donor]
    father = index_member.father
    mother = index_member.mother
    # check for 4 digit consistency
    mm4 = check_consistency(4, calls[args.index_donor], calls.get(father),
                            calls.get(mother))
    # check for 2 digit consistency
    mm2 = check_consistency(2, calls[args.index_donor], calls.get(father),
                            calls.get(mother))
    num_parents = len({father, mother} - {'0'})
    # print result line
    print('\t'.join(map(str, [
        args.index_donor, num_parents, mm2 or 'OK', mm4 or 'OK'
    ])))
