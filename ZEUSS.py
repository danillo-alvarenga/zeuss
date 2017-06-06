#!/usr/bin/env python3
#
# ZEUSS: recogniZing gEnome seqUences in metagenomic aSSemblies
#
# Version 1.0.2 - June 6, 2017
#
# Copyright © 2017 Danillo Oliveira Alvarenga
#
# ZEUSS is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# ZEUSS is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for
# more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with ZEUSS. If not, see <http://www.gnu.org/licenses/agpl-3.0.html>.
#
import os
import sys
import csv
import argparse
from csv import reader
from time import strftime

# Get arguments from the command line.
parser = argparse.ArgumentParser(description=
                                 "Kraken-based genomes retriever",
                                 formatter_class=lambda prog: 
                                 argparse.HelpFormatter(prog,
                                 max_help_position=100, width=100))

parser.add_argument("-v", "--version", action="version",
                    version="%(prog)s 1.0.2", help="show version and exit")

parser.add_argument("-f", "--file", metavar="Sequences.fasta",
                    required=True,
                    help="assembled metagenomic sequences")
parser.add_argument("-k", "--kraken", metavar="Kraken.output",
                    required=True,
                    help="Kraken assignment file")
parser.add_argument("-r", "--report", metavar="Kraken.report",
                    required=True,
                    help="Kraken report file")

m_excl = parser.add_mutually_exclusive_group(required=True)

m_excl.add_argument("-t", "--target", metavar="Taxon",
                    help="target taxon to retrieve sequences from")
m_excl.add_argument("-i", "--ignore", metavar="Taxon",
                    help="taxon to ignore")
m_excl.add_argument("-a", "--all", action="store_true",
                    help="retrieve all identified genomes")
parser.add_argument("-m", "--minimum", metavar="Mb", type=float,
                    help="minimum genome size for retrieval")
parser.add_argument("-x", "--maximum", metavar="Mb", type=float,
                    help="maximum genome size for retrieval")
parser.add_argument("-s", "--sequences", metavar="#", type=int,
                    help="maximum sequence number for a retrieved genome")
parser.set_defaults(minimum=0, maximum=0, sequences=1000)

args = parser.parse_args()

# Get filename and extension from the file argument.
filename, extension = os.path.splitext(os.path.basename(args.file))

# Allow maximum size for csv files.
csv.field_size_limit(sys.maxsize)

# Retrieve IDs from a hierarchical level according to the taxon input.
def get_IDs(taxon):

    taxon_IDs = []
    target_hierarchy = None
    current_hierarchy = 0

    with open(args.report) as report:

        for line in reader(report, delimiter = "\t"):

            line_items = list(line)
            target = line_items[5]

            if not target_hierarchy and taxon not in target:
                continue

            elif not target_hierarchy and taxon in target:
                taxon_IDs.append(line_items[4])
                target_hierarchy = len(target) - len(target.lstrip(' '))
                continue

            elif target_hierarchy:
                current_hierarchy = len(target) - len(target.lstrip(' '))
                if int(target_hierarchy) < int(current_hierarchy):
                    taxon_IDs.append(line_items[4])
                else:
                    break

    return taxon_IDs

# Find sequences to retrieve.
def get_headers(taxon, mode):

    taxon_headers = []
    header_IDs = get_IDs(taxon)

    with open(args.kraken, "rt") as kraken:

        for line in reader(kraken, delimiter = "\t"):

            line_items = list(line)

            if mode is "retrieve" and taxon == "root" and line_items[0] != 'U':
                taxon_headers.append('>' + line_items[1] + "\n")
            elif mode is "retrieve" and line_items[2] in header_IDs:
                taxon_headers.append('>' + line_items[1] + "\n")
            elif mode is "ignore" and line_items[2] not in header_IDs:
                taxon_headers.append('>' + line_items[1] + "\n")

    return taxon_headers

# Use the headers and the original fasta file to retrieve sequences
# either identified as the target taxon or not according to user request.
def retrieve_sequences(target, mode):

    nucleotides = 0
   
    if mode is "retrieve":
        taxon_name = target.replace('/', '|')
    elif mode is "ignore":
        taxon_name = target.replace('/', '|') + "_ignored"

    genome_filename = filename + "_" + taxon_name.replace(' ', '_') + extension
    headers = get_headers(target, mode)

    with open(args.file) as fasta, \
         open("zeuss.tmp", "w+t") as singlelines, \
         open(genome_filename, "w+t") as sequences:

        # Transform fasta into a single lines file to make
        # getting sequences easier.
        singlelines.write(fasta.readline())

        for line in fasta:
            if '>' in line:
                singlelines.write("\n" + line)
            else:
                singlelines.write(line.rstrip())

        singlelines.seek(0)

        # Check if a header is listed as a target and write headers
        # and sequences with the GenBank 70 character limit.
        for line in singlelines:

            if '>' in line and line in headers:

                sequences.write(line)

                seq = next(singlelines)
                nucleotides += len(seq.rstrip())
                seq = [seq[n:n+70] + "\n" for n in range(0, len(seq), 70)]

                for item in seq:
                    sequences.write(item)

    os.remove("zeuss.tmp")

    return len(headers), nucleotides, genome_filename

# Create a list of identified taxa.
def list_known_genomes():

    classified = []
    known = []

    # Grab taxon ID from each identified sequence.
    with open(args.kraken, "rt") as kraken:

        for line in kraken:

            line = line.split("\t")

            if 'U' in line[0]:
                continue
            elif 'C' in line[0] and line[2] not in classified:
                classified.append(line[2])

    # Create list of taxa based on the report.
    with open(args.report, "rt") as report:

        for line in report:

            line = line.split("\t")

            if line[4] in classified:
                known.append(line[5].strip())

    return known

# Group known sequences into potential genomes.
def retrieve_all(minimum, maximum, sequences):

    genomes_list = list_known_genomes()
    minimum = minimum * 1000000
    maximum = maximum * 1000000
    no_genomes = True

    for item in sorted(genomes_list, key=str.lower):

        genome = retrieve_sequences(item, "retrieve")
        retrieved = True

        # Exclude genomes above the sequence limit.
        if genome[0] > sequences:
            os.remove(genome[2])
            continue

        # Exclude genomes under the minimum or above the maximum expected size.
        if minimum and genome[1] < minimum:
                os.remove(genome[2])
                retrieved = False
        if maximum and genome[1] > maximum:
                os.remove(genome[2])
                retrieved = False

        if retrieved:
            no_genomes = False
            print (strftime("%c") + "\t" + item + " genome found with " +
                   format(genome[0], ",d") + " sequences and " +
                   format(genome[1], ",d") + " bases.\n")

    if no_genomes:
        print (strftime("%c") + "\tDone. No genomes were found.\n")

    return

# Run functions according to corresponding arguments.
def main():

    try:
        if args.target:
            print(strftime("%c") + "\tRetrieving " + args.target + " sequences.")
            genome = retrieve_sequences(args.target, "retrieve")
            print (strftime("%c") + "\tDone. " +
                   format(genome[0], ",d") + " sequences found, with " +
                   format(genome[1], ",d") + " bases.")

        elif args.ignore:
            print(strftime("%c") + "\tIgnoring " + args.ignore + " sequences.")
            genome = retrieve_sequences(args.ignore, "ignore")
            print (strftime("%c") + "\tDone. " +
                   format(genome[0], ",d") + " sequences found, with " +
                   format(genome[1], ",d") + " bases.")

        elif args.all:
            if args.minimum and args.maximum:
                print(strftime("%c") + "\tRetrieving genomes between " +
                   str(args.minimum) + " and " + str(args.maximum) + " Mb.\n")
            elif args.minimum:
                print(strftime("%c") + "\tRetrieving genomes larger than " +
                                                 str(args.minimum) + " Mb.\n")
            elif args.maximum:
                print(strftime("%c") + "\tRetrieving genomes smaller than " +
                                                 str(args.maximum) + " Mb.\n")
            else:
                print(strftime("%c") + "\tRetrieving all identified genomes.\n")
            retrieve_all(args.minimum, args.maximum, args.sequences)

    except KeyboardInterrupt:
        print("\n" + strftime("%c") + "\tProgram cancelled.\n")
    except:
        print(strftime("%c") + "\tError. Please verify input files.\n")

if __name__ == "__main__":
    main()
