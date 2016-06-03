# HLA-MA

<img align="right" width="171" height="200" src="https://raw.githubusercontent.com/bihealth/hlama/master/images/alpaca.png?token=AAf2NHKthW5G4gX1PY34OGhyaafRHSPRks5XWoJTwA%3D%3D">

HLA-MA allows for the matching of high-throughput sequencing (HTS) samples based on HLA typing.
Given a list of matches tumor/normal samples or a list of pedigree files with samples, HLA-MA validates the matching information.

## For the impatient

### Installation

- Install YARA
- Install RazerS3
- Install OptiType

```
# pip install hlama
```

### Checking matched tumor/normal samples

The input is a TSV file (actually whitespaces are also recognized as delimiters) listing the donor/patient name, the sample name, a classification of the sample into normal or tumor (N or T), and a comma-separated list of FASTQ files.
Files ending in `_1.fq.gz` and `_2.fq.gz` are recognized as first and second reads of a paired-end read run, as are files containing `_R1_` and `_R2_`.

```
# cat <<"EOF" >matched.tsv
donor sample-N  N normal_1.fq.gz,normal_2.fq.gz
donor sample-T1 T tumor_1.fq.gz,tumor_1.fq.gz
donor sample-T2 T metastasis_1.fq.gz,metastasis_2.fq.gz
EOF

# hlama --help

# hlama --tumor-normal matched.tsv --read-base-dir path/to/reads
```

### Checking germline data in pedigrees

The input is a PED file with an extra column for the read names.
The columns are family name, donor name, father name, mother name, sex (0 unknown, 1 male, 2 female), disease status (0 unknown, 1 unaffected, 2 affected), read names.
Actually, the sex and disease columns are ignored.
Files ending in `_1.fq.gz` and `_2.fq.gz` are recognized as first and second reads of a paired-end read run, as are files containing `_R1_` and `_R2_`.

```
cat <<"EOF" >pedigree.ped
FAM offspring father mother 1 2 offspring_1.fq.gz,offspring_2.fq.gz
FAM father 0 0 1 1 father_1.fq.gz,father_2.fq.gz
FAM mother 0 0 2 1 mother_1.fq.gz,mother_2.fq.gz
EOF

# hlama --help

# hlama --pedigree pedigree.ped --read-base-dir path/to/reads
```

## How does it work?

HLA-MA uses the third-party tools [OptiType](https://github.com/FRED-2/OptiType) (together with [Yara](https://www.seqan.de/apps/yara/) and [RazerS 3](https://www.seqan.de/apps/razers-3/)) for predicting the HLA types of a sample.
The [Human leukocyte antigen (HLA)](https://en.wikipedia.org/wiki/Human_leukocyte_antigen) is a gene complex important in the immune system.
The HLA loci are highly variable and are thus very useful as a genetic fingerprint for identifying samples.

There are three genes, HLA-A, HLA-B, HLA-C.
Thus, a diploid human genome carries six HLA gene copies in total.
Most HLA types found in the human population are known and are assigned a number, its HLA type, e.g., **HLA-A\*02:01**.
The combinatio of the six hla types in a human genome is used as the fingerprint.

**In matched tumor/normal samples** the HLA type should be the same, or in the case of somatic mutations in the HLA loci at least very similar.
Thus, a strong mismatch in HLA types indicates problems with sample matching (e.g., sample swaps).

**In samples derived from related individuals** the HLA types should follow the Mendelian inheritance rules.
Thus, for each offspring, one copy of HLA-A should come from the biological mother and the other copy should come from the biological father (and similar for HLA-B and HLA-C).

For OptiType, we observe an accuracy of 98% in HLA typing, thus its results can be used for easy sanity checking of HTS samples.
Generally, one considers the so-called two-digit HLA type (e.g., **HLA-A\*02**) and the so-called four-digit HLA type (e.g., **HLA-A\*02:01**).
When there is a single mismatch in the four-digit HLA type between the actual and expected types of a sample, a two-digit match can still indicate a good match.


## Reference

- Messerschmidt C., Beule D., Holtgrewe, M. (2016). Simple yet powerful matching of samples using HLA typing results. To appear.

## Frequently asked questions

**Q:** Should I use single-end data or paired-end data?<br>
**A:** Both can be used but we observe much better precision in OptiType with paired-end data.<br>

**Q:** The image you are using is an alpaca!<br>
**A:** That's true but lamas and alpacas are closely related.<br>
