# -*- coding: utf-8 -*-
"""Configuration management for hlama

Currently, there are three different possible sources for the dependencies
of HLA-MA.

- Assume that the software is available in $PATH
- The software is installed using Bioconda and in the environment
  hlama-$version
- The software is available using environment modules
"""

import configparser

__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'


class Configuration:
    """Helper class for accessing configuration"""

    @classmethod
    def load(klass, path):
        config = configparser.ConfigParser()
        config.read(path)
        return Configuration(config)

    def __init__(self, config):
        """Load configuration with values from the given path"""
        self.config = config

    @property
    def dep_source(self):
        return self.config.get('hlama', 'dep_source', fallback='in_path')

    def cmd_prefix(self):
        """Return necessary command prefix"""
        if self.dep_source == 'bioconda':
            prepend = self.config.get('hlama.bioconda', 'prepend_path')
            if prepend:
                prepend = 'export PATH={prepend}:$PATH; '.format(
                    prepend=prepend)
            env = self.config.get('hlama.bioconda', 'env')
            if env:
                s = '{}source activate {}'.format(
                    prepend if prepend else '', env)
            else:
                s = 'echo "Error: not configured" 1>&2; exit 1;'
            return '# Load conda environment\n{}\n{}'.format(
                prepend if prepend else '', s)
        elif self.dep_source == 'environment_modules':
            s = self.config.get(
                'hlama.environment_modules', 'module_command',
                fallback='echo "Error not configured" 1>&2; exit 1;')
            return '# Load environment modules\n{}'.format(s)
        else:
            return '# Dependencies are assumed to be in env PATH'
