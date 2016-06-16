#!/bin/bash

set -x

mason=/scratch/cubi/cmesser/biotools/mason/mason-0.1.2-Linux-x86_64/bin/mason
$mason illumina -mp -n 101 -N 1500 -sq donor1_dna_6_alleles.fasta -o donor1_normal.fq -ll 300 -le 60
$mason illumina -mp -n 101 -N 1500 -sq donor1_dna_6_alleles.fasta -o donor1_tumor.fq -ll 300 -le 60

$mason illumina -mp -n 101 -N 1500 -sq donor1_rna_6_alleles.fasta -o donor1_tumor_rna.fq -ll 300 -le 60
$mason illumina -mp -n 101 -N 1500 -sq donor1_rna_6_alleles.fasta -o donor1_tumor_rna.fq -ll 300 -le 60

$mason illumina -mp -n 101 -N 1500 -sq donor2_dna_6_alleles.fasta -o donor2_normal.fq -ll 300 -le 60
$mason illumina -mp -n 101 -N 1500 -sq donor2_dna_6_alleles.fasta -o donor2_tumor.fq -ll 300 -le 60

rm *.sam
