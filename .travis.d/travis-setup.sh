#!/bin/bash
set -ex

SCRIPT_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

# Install Miniconda 2, for dependencies

curl https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh \
    >/tmp/Miniconda2-latest-Linux-x86_64.sh
bash /tmp/Miniconda2-latest-Linux-x86_64.sh -b -p ~/miniconda2

export PATH=~/miniconda2/bin:${PATH}
conda config --add channels r
conda config --add channels bioconda

conda create -y -n hlama-0.1 yara=0.9.6 razers3=3.5.0 optitype=2015.10.20

# Install HLA-MA

pip3 install -r requirements.txt
python3 setup.py install

# Setup HLA-MA configuration

cat <<"EOF" >~/.hlama.cfg
[hlama]
# Allowed values for dep_source are
#
# - in_path (all binaries in $PATH, no further configuration
#   is required)
# - bioconda installed (using Bioconda (Python 2 for Optitype) see below)
# - environment_modules (available using environment modules see below)
dep_source = bioconda

# If hlama.dependencies is "bioconda" then this section is used for
# further configuration of the Bioconda setup.
[hlama.bioconda]
# Optional, value to prepend to $PATH for activating conda installation
prepend_path = ~/miniconda2/bin
# Name of the Conda environment to use.
env = hlama-0.1

# If hlama.dependencies is "environment_modules] then this section is
# used for further configuration in the Environment Modules setup.
[hlama.environment_modules]
# Lines to prepend to running the optitype command.  Note that you can use
# multi-line strings as long as the lines starting from the second line are
# indented.
module_command = # load modules
    module purge  # get rid of possible Python 3 module
    module load yara/0.9.4
    module load razers3/3.5.0
    module load optitype/2015.10.20
EOF
