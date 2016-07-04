#! /usr/bin/env python

import os, stat, os.path, time, datetime, subprocess
import re, sys, glob, argparse, csv, shutil, fileinput
from collections import defaultdict
from pprint import pprint
from itertools import islice
import ConfigParser

def __main__():
    print "script starts at: %s\n" % datetime.datetime.now()   
    args = parse_args()
    strain_list = "strains.txt"
    patient_list = "HIV_Cervical_patients.txt"
    integration_summary = args.integration_summary_file
    reformated_summary = ".".join([integration_summary, "formated"])
    statistics_file = '.'.join([reformated_summary, 'statistics'])

    strains = make_list(strain_list)
    patients = make_list(patient_list)

    integrations = make_integration_dict(integration_summary)
    statistics = write_integrations(reformated_summary, integrations,
                                    strains, patients, statistics_file)
    write_statistics(statistics, statistics_file)


def parse_args():
    parser = argparse.ArgumentParser(
        description='post-processing integration for comut plot!')
    parser.add_argument(
        '-i', '--integration_summary_file',
        help='specify filtered integration summary file',
        required=True)
    args = parser.parse_args()
    return args


def make_list(infile):
    print "infile is: ", infile
    items = []
    with open(infile, 'r') as fh:
        for line in fh:
            item = line.split()[0]
            items.append(item)
        #items = list(set(items))
        print items
    return items

def make_integration_dict(integration_summary):
    integrations = dict()
    print "The integration summary file is: %s." % integration_summary
    with open(integration_summary, 'r') as fh:
        records = csv.DictReader(fh,  delimiter='\t')
        for line in records:
            strain = "_".join(line['virus'].split(' '))
            patient = line["patient"]
            integration = line["Integration"]
            try:
                integrations[strain][patient].append(integration)
            except KeyError:
                if strain not in integrations:
                    integrations[strain] = {}
                if patient not in integrations[strain]:
                    integrations[strain][patient] = [integration]
    pprint(integrations)
    return integrations


def write_integrations(reformated_summary, integrations,
                       strains, patients, statistics_file):
    statistics = []
    with open(reformated_summary,  'wb') as fh:
        headers = ['strain', 'patient', 'integration']
        writer2 = csv.writer( fh, delimiter='\t' )
        writer2.writerow(headers)
        for strain in strains:
            num_patients = 0
            integration_statuses = []
            for patient in patients:
                integration = 'not_detected'
                if strain in integrations and patient in integrations[strain]:
                    num_patients = len(integrations[strain])
                    status = list(set(integrations[strain][patient]))
                    integration_statuses.append(status)
                    if (len(status) > 1):
                        integration = "multiple"
                    else:
                        integration = status[0]
                        if integration == 'YES':
                            integration = 'integrated'
                        if integration == 'NO':
                            integration = 'unintegrated'
                writer2.writerow([strain, patient, integration])
            (num_integrated,
             num_unintegrated) = get_integration_statistics(integration_statuses)
            statistics.append([strain, num_patients,
                               num_integrated, num_unintegrated])
    return statistics


def write_statistics(statistics, statistics_file):
    with open(statistics_file, 'wb') as opf:
        headers = ['strain', 'number_patients',
                   'number_integrated', 'number_unintegrated']
        writer1 = csv.writer(opf, delimiter='\t')
        writer1.writerow(headers)
        for item in statistics:
            writer1.writerow(item)

def get_integration_statistics(integration_statuses):
    # figure out statistics for each strain
    final_status = [i[0] for i in integration_statuses]
    num_integrated = final_status.count('YES')
    num_unintegrated = final_status.count('NO')
    return [num_integrated, num_unintegrated]


if __name__ == '__main__':
    __main__()
 
