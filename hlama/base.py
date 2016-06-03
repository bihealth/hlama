# -*- coding: utf-8 -*-
"""Code usable for both somatic and pedigree sample checking"""

import re


class HLAType:
    """Representation of an HLA type (up to 4 digits)"""

    @classmethod
    def parse(klass, hla_str):
        m = re.match(r'(?:HLA-)?([ABC]+)(?:\*(\d+)(?::(\d+))?)?', hla_str)
        if not m:
            raise RuntimeError('HLA string invalid {}'.format(hla_str))
        return HLAType(*list(m.groups()))

    def __init__(self, gene_name, two_digits=None, four_digits=None):
        self.gene_name = gene_name
        self.two_digits = two_digits
        self.four_digits = four_digits

    def __lt__(self, other):
        return ((self.gene_name, self.two_digits, self.four_digits) <
                (other.gene_name, other.two_digits, other.four_digits))

    def __eq__(self, other):
        return ((self.gene_name, self.two_digits, self.four_digits) ==
                (other.gene_name, other.two_digits, other.four_digits))

    def __hash__(self):
        return (hash(self.gene_name) ^ hash(self.two_digits) ^
                hash(self.four_digits))

    def same_gene(self, other):
        """Return whether the genes equal"""
        return self.gene_name == other.gene_name

    def equal_two_digits(self, other):
        """Return whether equal to two digits"""
        return (self.same_gene(other) and
                self.two_digits == other.two_digits)

    def equal_four_digits(self, other):
        """Return whether equal to four digits"""
        return (self.equal_two_digits(other) and
                self.four_digits == other.four_digits)

    def prec_str(self, precision):
        """Precision string"""
        assert precision in (0, 2, 4)
        if precision == 4 and not self.four_digits:
            precision = 2
        if precision == 2 and not self.two_digits:
            precision = 0
        if precision == 4:
            return ('HLA-{self.gene_name}*{self.two_digits}:'
                    '{self.four_digits}').format(self=self)
        elif precision == 2:
            return 'HLA-{self.gene_name}*{self.two_digits}'.format(self=self)
        else:
            return 'HLA-{self.gene_name}'.format(self=self)

    def __str__(self):
        """Return string label for HLA type"""
        if self.four_digits:
            return ('HLA-{self.gene_name}*{self.two_digits}:'
                    '{self.four_digits}').format(self=self)
        elif self.two_digits:
            return 'HLA-{self.gene_name}*{self.two_digits}'.format(self=self)
        else:
            return 'HLA-{self.gene_name}'.format(self=self)
