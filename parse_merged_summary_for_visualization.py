#!/usr/bin/env python

import os
import stat
import os.path
import time
import datetime
import subprocess
import re
import sys
import glob
import argparse
import csv
from collections import defaultdict
from pprint import pprint
from itertools import islice
import fileinput
import shutil


def parse_merged_summary(infile, genes):
    # print "infile is: %s" % infile
    with open(infile) as fh:
        records = csv.DictReader(fh,  delimiter='\t')
        headers = records.fieldnames
        # print "xxxx", headers
        # make a gene_pos_dict to get the 1st integrations position for the gene
        gene_positions = dict()
        for line in records:
            patient = line[headers[0]]
            integrated = line[headers[2]] 
            virus = line[headers[1]]
            chromosome = line[headers[3]]
            DNA_positions = [i.split(',')[0] for i in line[headers[5]].split(';')] 
            RNA_positions = [i.split(',')[0] for i in line[headers[7]].split(';')] 
            DNA_integration_details = line[headers[5]].split(';')
            RNA_integration_details = line[headers[7]].split(';')
            if len(DNA_integration_details) > 1: # integrated
                DNA_genes = [i.split(',')[1:] for i in DNA_integration_details] 
                # print DNA_positions, DNA_genes 
                for i in DNA_positions:
                    # print i, DNA_genes[DNA_positions.index(i)]
                    all_DNA_genes = DNA_genes[DNA_positions.index(i)]
                    for gene in all_DNA_genes:
                        if gene in genes:
                            # print i, gene
                            if gene not in gene_positions:
                                gene_positions[gene] = i
            if len(RNA_integration_details) > 1: # integrated
                RNA_genes = [i.split(',')[1:] for i in RNA_integration_details]
                # print RNA_positions, RNA_genes
                for i in RNA_positions:
                    all_RNA_genes = RNA_genes[RNA_positions.index(i)]
                    for gene in all_RNA_genes:
                        if gene in genes:
                            # print i, gene
                            if gene not in gene_positions:
                                gene_positions[gene] = i
            # print chromosome, DNA_positions, RNA_positions
            for pos in DNA_positions:
                if len(pos.split('_')) == 2: # integrated
                    chr, pos = pos.split('_')
                    # print patient, chr, pos, '_'.join(['HPV', virus.split('type ')[-1]])
            for pos in RNA_positions:
                if len(pos.split('_')) == 2: # integrated
                    chr, pos = pos.split('_')
                    # print patient, chr, pos, '_'.join(['HPV', virus.split('type ')[-1]])
    # print gene_positions
    print '\t'.join(['Chromosome', 'Position', 'gene'])
    for gene in gene_positions:
        chr, pos =  gene_positions[gene].split('_')
        print '\t'.join([chr, pos, gene])

        
def get_list(infile):
    a = []
    with open (infile, 'r') as fh:
         for line in fh:
             sl = line.split()
             a.append(sl[0])
    # print a
    return a


def parse_args():
    parser = argparse.ArgumentParser(
        description='Merge DNA and RNA integration summary files')
    parser.add_argument('-i', '--merged_input_file',
                        help='specify DNA integration summary file',
                        required=True)
    args = parser.parse_args()
    return args


def __main__():
    # print "Scripts starts at: %s!" % datetime.datetime.now()     
    args = parse_args()
    gene_file = "/projects/trans_scratch/validations/workspace/szong/Cervical/integration/interested_genes.txt"
    genes = get_list(gene_file)
    merged_input_file = args.merged_input_file
    parse_merged_summary(merged_input_file, genes)


if __name__ == '__main__':
    __main__()

