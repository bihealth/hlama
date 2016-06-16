#!/bin/bash

mason=/scratch/cubi/cmesser/biotools/mason/mason-0.1.2-Linux-x86_64/bin/mason
$mason illumina -mp -n 101 -N 1500 -sq donor1_dna_6_alleles.fasta -o donor1_normal.fq
$mason illumina -mp -n 101 -N 1500 -sq donor1_dna_6_alleles.fasta -o donor1_tumor.fq



rm *.sam
