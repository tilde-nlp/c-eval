import sys
import os
import math
import argparse
from collections import defaultdict


def get_alignments(words_s, words_t, alignments):
    for alignment in alignments:
        left, right = alignment.split('-')
        yield (words_s[int(left)], words_t[int(right)])


parser = argparse.ArgumentParser(description='Extracts feature values from Giza++ output')
parser.add_argument('-s', '--source-file', help='Source corpus file')
parser.add_argument('-t', '--target-file', help='Target corpus file')
parser.add_argument('-fa', '--fast-align-table', help='Fast-align table for source alignments')
parser.add_argument('-als', '--alignmnets', help='Src to trg file', required=True)
parser.add_argument('-o', '--output-file', help='Output file')
args = parser.parse_args()


probs_file = open(args.output_file + ".probabilities.txt", 'w')


vocab = defaultdict(int)
probs = defaultdict(lambda: defaultdict(float))

csrc = open(args.source_file, 'r')
ctrg = open(args.target_file, 'r')
table = open(args.fast_align_table, 'r')
als = open(args.alignments, 'r')



#Uztaisa src vocab
for line in table:
    values = line.split()
    if values[0] not in vocab: vocab[values[0]] = len(vocab)
    if values[1] not in vocab: vocab[values[1]] = len(vocab)
    probs[vocab[values[0]]][vocab[values[1]]] = float(values[2])

alignments_line = " "

while True:
    if not alignments_line:
            break

    alignments_line = als.readline() # Ielasa kartejo alignmnets liniju
    alignments = alignments_line.split()

    words_line_src = csrc.readline().split() #Ielasa kartejo teskta liniju
    words_line_trg = ctrg.readline().split()

    pairs_src = list(get_alignments(words_line_src, words_line_trg, alignments)) #Dabon vardu pariti
    # Atrod vardnica para rezultatu, ieraksta failaa
    for pair in pairs_src:
        probs_file.write(str(probs[vocab[pair[0]]][vocab[pair[1]]]) + ' ')
    probs_file.write('\n')

table.close()
probs_file.close()
csrc.close()
ctrg.close()
als.close()

