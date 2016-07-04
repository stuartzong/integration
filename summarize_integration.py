#! /usr/bin/env python

import os
import os.path
import datetime
import argparse
import csv
import logging

import colorlog

import ConfigParser

logger = colorlog.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
handler.setFormatter(
    colorlog.ColoredFormatter('%(log_color)s%(levelname)s:%(name)s:%(message)s'))
logger.addHandler(handler)



def parse_integration_result(integration_summary_file):
    with open(integration_summary_file, 'r') as fh:
        records = csv.DictReader(fh,  delimiter='\t')
        headers = records.fieldnames
        for line in records:



def quality_filtering(variant_summary, thresholds, filtered_summary):
    with open('out.tmp', 'wb') as fh_tmp:
        writer_tmp = csv.writer(fh_tmp, delimiter='\t')
        with open(filtered_summary,  'wb') as fh:
            writer = csv.writer(fh, delimiter='\t')
            with open(variant_summary, 'r') as handle:
                records = csv.DictReader(handle,  delimiter='\t')
                headers = records.fieldnames
                writer.writerow(headers)
                for line in records:
                    assign_numeric_type(line)
                    content = [line[i] for i in headers]
                    if  pass_quality_filters(thresholds, line):
                        writer.writerow(content)
                    else:
                        writer_tmp.writerow(content)


def make_occurrence_dict(infile):
    gene_patients = {}
    var_patients = {}
    gene_variants = {}
    with open (infile) as fh:
        records = csv.DictReader(fh,  delimiter='\t')
        for line in records:
            gene = line['gene']
            patient = line["patient_ID"].split('_')[0]
            variant = '_'.join([gene,
                                line["chromosome"],
                                line["position"],
                                line["ref_base"],
                                line["alt_base"]])
            try:
                gene_patients[gene].append(patient)
            except KeyError:
                gene_patients[gene] = [patient]
            try:
                var_patients[variant].append(patient)
            except KeyError:
                var_patients[variant] = [patient]
            try:
                gene_variants[gene].append(variant)
            except KeyError:
                gene_variants[gene] = [variant]
    # remove duplicate items
    for gene in gene_patients:
        gene_patients[gene] = len(list(set(gene_patients[gene])))
    #print gene_patients
    for variant in var_patients:
        var_patients[variant] = len(list(set(var_patients[variant])))
    #pprint(var_patients)
    for gene in gene_variants:
        gene_variants[gene] = len(list(set(gene_variants[gene])))
    #print gene_variants
    return [gene_patients, var_patients, gene_variants]


                                   
def parse_args():
    parser = argparse.ArgumentParser(
        description='Filter variants based on qulaity and somatic filters')
    parser.add_argument(
        '-i', '--integration_summary_paths', required=True,
        help='specify input file, which contains all summary file paths.')
    args = parser.parse_args()
    return args


def main():
    start = datetime.datetime.now()
    logger.info("integration summarization script starts at: %s" % start)
    args = parse_args()
    integration_summary_paths = args.integration_summary_paths
    
    quality_filtering(args.input_file, thresholds, filtered_summary)
    if args.pairing == 'paired':
        logger.info('Filtering variants based on somatic filters!')
        somatic_filtering(filtered_summary, thresholds, somatic_summary)
    # recalculate occurrence for filtered summary
    # out = make_occurrence_dict(filtered_summary)
    (gene_patients_occur,
     var_patients_occur,
     gene_variants_occur) = make_occurrence_dict(filtered_summary)
    logger.info('Recalculate filtered variant occurrence!')
    calculate_occurrence(filtered_summary,
                         gene_patients_occur,
                         var_patients_occur,
                         gene_variants_occur)
    # recalculate occurrence for somatic summary
    if (os.path.isfile(somatic_summary)):
        # out = make_occurrence_dict(somatic_summary)
        (gene_patients_occur,
         var_patients_occur,
         gene_variants_occur) = make_occurrence_dict(somatic_summary)
        logger.info('Recalculate somatic variant occurrence!')
        calculate_occurrence(somatic_summary,
                             gene_patients_occur,
                             var_patients_occur,
                             gene_variants_occur)
        os.remove(somatic_summary)
    os.remove(filtered_summary)
    end = datetime.datetime.now()
    logger.info("Quality and somatic filtering script ends at: %s\n" % end)


if __name__ == '__main__':
    main()
