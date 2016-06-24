#!/bin/bash

set -x

mason=/scratch/cubi/cmesser/biotools/mason/mason-0.1.2-Linux-x86_64/bin/mason
$mason illumina -mp -n 101 -N 1500 -sq daughter1.fasta -o daughter1.fq -ll 300 -le 60
$mason illumina -mp -n 101 -N 1500 -sq father1.fasta -o father1.fq -ll 300 -le 60
$mason illumina -mp -n 101 -N 1500 -sq mother1.fasta -o mother1.fq -ll 300 -le 60

rm *.sam
