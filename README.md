# **recogniZing gEnome seqUences in metagenomic aSSemblies (ZEUSS)**

recogniZing gEnome seqUences in metagenomic aSSemblies (ZEUSS) is a program that takes Kraken's taxonomic assignments for assembled metagenomes and retrieves genome sequences of select taxa.

---

## RELEASE

Version 1.0.0 - Mar 16, 2017.

Available from <https://github.com/danillo-alvarenga/zeuss>.

---

## REQUIREMENTS

ZEUSS runs on Python 3.4+ and has been tested on Ubuntu 14.04 and 16.04. It should work on any modern GNU/Linux distro. No installation for this program is required. However, since it works on Kraken outputs, it is necessary to have access to a proper installation of the Kraken software and a suitable database to obtain the necessary files.

ZEUSS has been developed with Kraken version v0.10.5-beta and its minikraken database in mind. Please refer to the Kraken documentation for its installation instructions.

>**Note:** Older or newer versions of Kraken as well as other operating systems might also work, but since they have not been tested this is not guaranteed.

---

## USAGE

`ZEUSS [-h] [-v] -f Sequences.fasta -k Kraken.output -r Kraken.report (-t Taxon | -i Taxon | -a) [-m Mb] [-x Mb] [-s #]`  

optional arguments:

`-h`, `--help` | show a help message and exit  
`-v`, `--version` | show version and exit  

`-f Sequences.fasta`, `--file Sequences.fasta` | assembled metagenomic sequences  
`-k Kraken.output`, `--kraken Kraken.output` | Kraken assignment file  
`-r Kraken.report`, `--report Kraken.report` | Kraken report file  

`-t Taxon`, `--target Taxon` | target taxon to retrieve sequences from  
`-i Taxon`, `--ignore Taxon` | taxon to ignore  

`-a`, `--all` | retrieve all identified genomes  
`-m Mb`, `--minimum Mb` | minimum genome size for retrieval  
`-x Mb`, `--maximum Mb` | maximum genome size for retrieval  
`-s #`, `--sequences #` | maximum number of sequences for a retrieved genome  

In order to run ZEUSS, point it to the assembled metagenome fasta file, the Kraken taxonomic assignment output, and the Kraken database report file. Then, choose between retrieving the genome of a specific taxon from among the metagenome, removing the sequences of a specific taxon from the metagenome, or recovering genomes from all identified taxa. If you choose the latter, you may optionally provide values for minimum and/or maximum retrieved genome size in Mb and a maximum number of contigs/scaffolds allowed for each retrieved genome. By default, ZEUSS retrieves genomes broken into 1,000 contigs or less.

>**Note:** The indicated taxon name must be typed exactly as found in the database used by Kraken.

**Examples**:
- retrieve the genome of a single genus: `ZEUSS -f scaffolds.fasta -k scaffolds.kraken -r scaffolds.kraken.report -t Nostoc`
- exclude a phylum from the metagenome: `ZEUSS -f scaffolds.fasta -k scaffolds.kraken -r scaffolds.kraken.report -i Cyanobacteria`
- retrieve all genomes between 1 and 10 Mb that are broken into 100 sequences or less: `ZEUSS -f scaffolds.fasta -k scaffolds.kraken -r scaffolds.kraken.report -a -m 1 -x 10 -s 100`

---

## NECESSARY FILES

First, you need to get Kraken to generate taxonomic assignments for the target assembled metagenome. To do so, you can for example run Kraken with the minikraken database by issuing a command similar to this:
`kraken --db /path/to/minikraken --output assignments.kraken metagenome.fasta`

After the assignments are done, you need to generate a sample report. You should issue a command like this one:
`kraken-report --db /path/to/minikraken assignments.kraken > assignments.kraken.report`

Then you can feed both files to ZEUSS for selecting specific sequences in the assembly. Refer to the Kraken documentation for additional parameters and how to use alternative databases.

---

## RESULTS

If you provide a taxon to be retrieved (with the `--target` parameter), ZEUSS will select sequences in the metagenome assigned to that taxon and write them into a fasta file in the working directory. If you instead choose to ignore a taxon (with the `--ignore` parameter), ZEUSS will write a file containing every sequence but those identified as that taxon. In either case, the file written will be named after the original filename appended by the retrieved/ignored taxon name.

Keep in mind that ZEUSS works by grouping all sequences that are classified in a taxonomic level, from the highest to the lowest hierarchical point. For instance, if you specify a phylum to be retrieved, the output file will include all sequences identified in the different classes, orders, families, genera, species and strains that are classified in that phylum by the database provided to Kraken. Thus, sequences in files named as lower taxonomic levels should also have been included in files containing sequences of their corresponding higher taxonomic levels.

Beware that if you want to retrieve all identified genomes (by using the `--all` parameter), ZEUSS will output a number of fasta files equal to every taxonomic level identified, which means lots of files with overlapping sequences and manual curation. However, the `--minimum` and `--maximum` parameters will respectively exclude sequences for those taxa that do not add up to the minimum or surpass the maximum number of base pairs indicated. Additionally, the `--sequences` parameter will limit the output to genomes broken into a number of sequences under the provided contig/scaffold limit only.

---

## CITATION

If you find this software useful in your research, please cite the following:

- Alvarenga DO (2017) recogniZing gEnome seqUences in metagenomic aSSemblies (ZEUSS). Available from <https://github.com/danillo-alvarenga/zeuss>.

- Wood DE, Salzberg SL (2014) Kraken: ultrafast metagenomic sequence classification using exact alignments. Genome Biol 15:R46. DOI: <https://doi.org/10.1186/gb-2014-15-3-r46>.

---

## ISSUES AND REQUESTS

If you experience any issues or would like to see support for an additional feature implemented in ZEUSS, please file a request in the GitHub issue tracker or email it to the developer. Feel free to contact the developer with any further questions regarding this software. You can reach him at <mailto:danillo.alvarenga@gmail.com>.

---

## LICENSE

Copyright © 2017 Danillo Oliveira Alvarenga

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/agpl-3.0.html>.
