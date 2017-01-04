# Tutorial

To test if you have installed HLA-MA correctly, you can run it on the provided test data.

If you did not already, activate the conda environment

```
# source activate hlama
```

and download HLA-MA from github for the test data.

```
# git clone https://github.com/bihealth/hlama.git
```

Then, call HLA-MA:

```
# cd hlama
# hlama --tumor-normal tests/data/tumor_normal/donors.tsv  --work-dir TEST --reads-base-dir tests/data/tumor_normal --num-threads 4
```

Afterwards, you should find the following files and directories in ```TEST```:

```
data.json
donor1_normal.d
donor1_tumor.d
donor1_tumor_rna.d
donor2_normal.d
donor2_tumor.d
report.txt
Snakefile
tmp
```

with the HLA-MA results in ```report.txt``` and all optitype results in the directories suffixed with ```.d```.

```
# cat report.txt 
donor2_tumor    OK      OK
donor1_tumor    OK      OK
donor1_tumor_rna        OK      1
```
