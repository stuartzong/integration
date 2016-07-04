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

# dict: key -> info to be added 
def make_integration_dict(infile):
    print "infile is: %s" % infile
    with open(infile) as fh:
        integrations = dict()
        records = csv.DictReader(fh,  delimiter='\t')
        headers = records.fieldnames
        print "xxxx", headers
        for line in records:
            patient = line[headers[0]]
            virus = line[headers[2]]
            chromosome = line[headers[4]].split("_")[0]
            integration = '_'.join([line[headers[3]], chromosome])
            details = '&'.join([line[i] for i in headers])
            try:
                integrations[patient][virus][integration].append(details)
            except KeyError:
                if patient not in integrations:
                    integrations[patient] = {}
                if virus not in integrations[patient]:
                    integrations[patient][virus] = {}
                if integration not in integrations[patient][virus]:
                    integrations[patient][virus][integration] = [details]
    pprint(integrations)
    return integrations

def merge_nested_dicts(DNA_integrations, RNA_integrations, patient_ids):
    outfile = 'merged_integration_results.txt'
    writer = csv.writer(open(outfile, 'wb'), delimiter='\t')
    writer.writerow(['patient', 'virus', 'integrated', 'chromosome', 'DNA_lib', 'DNA_details', 'RNA_lib', 'RNA_details'])
    patients = set(DNA_integrations.keys() + RNA_integrations.keys())
    for patient in patients:
        # print patient
        viruses = set(DNA_integrations[patient].keys() + RNA_integrations[patient].keys())
        if 'No-Hits' in viruses:
            viruses.remove('No-Hits')
        for virus in viruses:
            # print patient, virus
            try:
                DNA_integration = DNA_integrations[patient][virus].keys()
            except KeyError:
                DNA_integration = []
                # print patient, virus, 'not in DNA_integrations'
            try:
                RNA_integration = RNA_integrations[patient][virus].keys()
            except KeyError:
                RNA_integration = []
                # print patient, virus, 'not in RNA_integrations'
            integrations = set(DNA_integration + RNA_integration)

            for integration in integrations:
                integrated_all = [i.split('_')[0] for i in integrations]
                integrated, chr = integration.split('_')
                DNA_lib = patient_ids[patient][0]
                RNA_lib = patient_ids[patient][1]
                if integrated == 'NO' and 'YES' not in integrated_all:# need to check this line
                    print DNA_integration, len(DNA_integration), RNA_integration, len(RNA_integration)
                    DNA_tmp = '&&'.join(DNA_integration)
                    RNA_tmp = '&&'.join(RNA_integration)
                    print 'mmmmmmmmmmmmmmmmmm'
                    print integration, DNA_integration 
                    if 'YES' in DNA_tmp:
                        DNA_details = 'integrated_in_DNA'
                    elif 'NO' in DNA_tmp:
                        DNA_details = 'detected_but_not_integrated_in_DNA'
                    else:
                        DNA_details = 'not_detected_in_DNA'
 
                    if 'YES' in RNA_tmp:
                        RNA_details = 'integrated_in_RNA'
                    elif 'NO' in RNA_tmp:
                        RNA_details = 'detected_but_not_integrated_in_RNA'
                    else:
                        RNA_details = 'not_detected_in_RNA'
                if integrated == 'YES':
                    # print DNA_integration, len(DNA_integration), RNA_integration, len(RNA_integration)
                    DNA_tmp = '&&'.join(DNA_integration)
                    RNA_tmp = '&&'.join(RNA_integration)
                    # print 'mmmmmmmmmmmmmmmmmm'
                    # print integration, DNA_integration 
                    if 'YES' in DNA_tmp:
                        DNA_details = 'integrated_in_DNA_but_not_on_chr%s' % chr
                        if integration in DNA_integration:
                            DNA_details = DNA_integrations[patient][virus][integration]
                            DNA_details = ';'.join([','.join(i.split('&')[4:]) for i in DNA_details])
                    elif 'NO' in DNA_tmp:
                        DNA_details = 'detected_but_not_integrated_in_DNA'
                    else:
                        DNA_details = 'not_detected_in_DNA'
 
                    if 'YES' in RNA_tmp:
                        RNA_details = 'integrated_in_RNA_but_not_on_chr%s' % chr
                        if integration in RNA_integration:
                            RNA_details = RNA_integrations[patient][virus][integration]
                            RNA_details = ';'.join([','.join(i.split('&')[4:]) for i in RNA_details])
                    elif 'NO' in RNA_tmp:
                        RNA_details = 'detected_but_not_integrated_in_RNA'
                    else:
                        RNA_details = 'not_detected_in_RNA'
                print patient, virus, integrated, DNA_lib, DNA_details, RNA_lib, RNA_details
                writer.writerow([patient, virus, integrated, chr, DNA_lib, DNA_details, RNA_lib, RNA_details])


def get_library_ids(meta_file):
    with open(meta_file) as fh:
        patient_ids = dict()
        records = csv.DictReader(fh,  delimiter='\t')
        headers = records.fieldnames
        print "xxxx", headers
        for line in records:
            if 'normal' not in line[headers[4]].lower():
                patient = line[headers[0]]
                DNA_lib = line[headers[2]]
                RNA_lib = line[headers[5]]
            patient_ids[patient] = [DNA_lib, RNA_lib]
    return patient_ids


def parse_args():
    parser = argparse.ArgumentParser(
        description='Merge DNA and RNA integration summary files')
    parser.add_argument('-i1', '--DNA_input_file',
                        help='specify DNA integration summary file',
                        required=True)
    parser.add_argument('-i2', '--RNA_input_file',
                        help='specify RNA integration input file',
                        required=True)
    parser.add_argument('-i3', '--meta_file',
                        help='specify paitent and library id input file',
                        required=True)
    args = parser.parse_args()
    return args


def __main__():
    print "Scripts starts at: %s!" % datetime.datetime.now()     
    args = parse_args()
    DNA_input_file = args.DNA_input_file
    RNA_input_file = args.RNA_input_file
    meta_file = args.meta_file
    patient_ids = get_library_ids(meta_file)
    DNA_integrations = make_integration_dict(DNA_input_file)
    RNA_integrations = make_integration_dict(RNA_input_file)
    merge_nested_dicts(DNA_integrations, RNA_integrations, patient_ids)


if __name__ == '__main__':
    __main__()

