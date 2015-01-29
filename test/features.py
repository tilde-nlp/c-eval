import sys
import os
import math
import argparse
from collections import defaultdict

# based on ca-align-1.1.1.py retrieved on 2014-06-30


def extract_giza_alignments(line, reverse = False):
    length = len(line)
    alignments = []
    x = 0
    j = 8
    check = 0
    while j < length - 4:
        if line[j:j+2] == '({':
            x += 1
            j += 2
            check = 1
        if line[j:j+1].isdigit() and check == 1:
            k = j + 1
            while line[k:k + 1].isdigit() == True:
                k += 1
            if not reverse:
                alignments.append(str(int(line[j:k]) - 1) + '-' + str(x - 1))
            else:
                alignments.append(str(x - 1) + '-' + str(int(line[j:k]) - 1))
            j = k
        if line[j:j+2] == '})':
            check = 0
        j += 1
    return alignments


def extract_fastalign_alignments(line, mode):
    if mode == 'src':
        return line.split()
    elif mode == 'trg': 
        alignments_list = []
        for pair in line.split():
            split = pair.split('-')
            alignments_list.append(str(split[1] + '-' + split[0]))
        return alignments_list


def symmetrize_alignments_union(src, trg):
    if not src or not trg:
        return []
    
    alignments = []
    for s in src:
        #flog.write(str(s) + ' src \n')
        for t in trg:
            #flog.write(str(t) + '\n')
            if s == t:
                #flog.write(str(s) + ' == ' + str(s) + '\n')
                alignments.append(s)
    return alignments


def calculate_alignment(score_line, tokens):
    if len(score_line) > 0 and score_line[0] == '#' and ' : ' in score_line:
        f1 = float(score_line.split()[-1])
        f1 = math.pow(f1, 1/float(len(tokens)))
        f1 = math.log(f1)
        f1 = format_num(f1)
        return f1
    return 0


def calculate_sym_ratio(sym_alignments, lang_alignments):
    return float(len(sym_alignments)) / len(lang_alignments) if len(lang_alignments) != 0 else 0


def format_num(n, precision=5):
    return ('{0:0.' + str(precision) + 'f}').format(float(n))


def get_alignments(words_s, words_t, alignments):
    for alignment in alignments:
        left, right = alignment.split('-')
        yield (words_s[int(left)], words_t[int(right)])


def sum_src_pow(pairs, vocab, table):
    sum = 1.0
    for pair in pairs:
        sum = sum * table[vocab[pair[0]]][vocab[pair[1]]]
    return abs(sum)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Extracts feature values from Giza++ output')
    parser.add_argument('-a', '--aligner', help='Aligner used or input type', choices=['giza', 'fastalign'], default='giza')
    parser.add_argument('-s', '--source-file', help='Source corpus file')
    parser.add_argument('-t', '--target-file', help='Target corpus file')
    parser.add_argument('-st', '--source-target-file', help='Src to trg file', required=True)
    parser.add_argument('-ts', '--target-source-file', help='Trg to src file', required=True)
    parser.add_argument('-o', '--output-file', help='Output file')
    parser.add_argument('-l', '--log-file', help='Log file')
    parser.add_argument('-p', '--precision', help='Floating number precision', type=int)
    parser.add_argument('-n', '--lines', help='Number of sentences to process', type=int)
    parser.add_argument('-d', '--delimiter', help='Delimiter')
    parser.add_argument('-hdr', '--header', help='Print header')
    parser.add_argument('-c', '--class', dest='class_value', help='Add class column with the specified value')
    parser.add_argument('-fas', '--fast-align-table-source', help='Fast-align table for source alignments')
    parser.add_argument('-fat', '--fast-align-table-target', help='Fast-align table for target alignments')
    args = parser.parse_args()

    fout = open(args.output_file, 'w') if args.output_file != None else sys.stdout
    flog = open(args.log_file, 'w') if args.log_file != None else sys.stdout if fout != sys.stdout else open(os.devnull, 'w')

    alssrc = open(args.source_target_file, 'r')
    alstrg = open(args.target_source_file, 'r')

    aligner = args.aligner if args.aligner != None else 'giza'
    delimiter = args.delimiter.replace('\\t', '\t') if args.delimiter != None else ','
    print_header = args.header.lower() != 'false' if args.header != None else True
    max_lines = int(args.lines) if args.lines != None else None
    precision = int(args.precision) if args.precision != None else 5


    columns = ['AlignmentScoreSource', 'AlignmentScoreTarget', 'SymRatioSource', 'SymRatioTarget', 'q', 'w', 'u', 'i', 'p', 'a', 'd', 'f',]
    if aligner == 'fastalign':
        csrc = open(args.source_file, 'r')
        ctrg = open(args.target_file, 'r')
        tablesrc = open(args.fast_align_table_source, 'r')
        tabletrg = open(args.fast_align_table_target, 'r')

        vocab = defaultdict(int)
        probssrc = defaultdict(lambda: defaultdict(float))
        probstrg = defaultdict(lambda: defaultdict(float))

        for line in tablesrc:
            values = line.split()
            if values[0] not in vocab: vocab[values[0]] = len(vocab)
            if values[1] not in vocab: vocab[values[1]] = len(vocab)
            probssrc[vocab[values[0]]][vocab[values[1]]] = float(values[2])

        for line in tabletrg:
            values = line.split()
            if values[0] not in vocab: vocab[values[0]] = len(vocab)
            if values[1] not in vocab: vocab[values[1]] = len(vocab)
            probstrg[vocab[values[0]]][vocab[values[1]]] = float(values[2])

        tablesrc.close()
        tabletrg.close()

    if args.class_value: columns += ['class']
    line_num = 0

    if print_header:
        fout.write(delimiter.join(columns) + '\n')

    while max_lines == None or line_num < max_lines:
        if aligner == 'giza':
            score_line_src = alssrc.readline()
            score_line_trg = alstrg.readline()
            tokens_line_src = alssrc.readline()
            tokens_line_trg = alstrg.readline()
        elif aligner == 'fastalign':
            words_line_src = csrc.readline().split()
            words_line_trg = ctrg.readline().split()

        alignments_line_src = alssrc.readline()
        alignments_line_trg = alstrg.readline()
        
        if not alignments_line_src or not alignments_line_trg:
            break
        
        if aligner == 'giza':
            alignments_src = extract_giza_alignments(alignments_line_src)
            alignments_trg = extract_giza_alignments(alignments_line_trg, reverse=True)
        elif aligner == 'fastalign':
            alignments_src = alignments_line_src.split();
            alignments_trg = alignments_line_trg.split();
            alignments_trg_normalized = extract_fastalign_alignments(alignments_line_trg, 'trg')
            pairs_src = list(get_alignments(words_line_src, words_line_trg, alignments_src))
            pairs_trg = list(get_alignments(words_line_trg, words_line_src, alignments_trg))

            sum_src = 0
            for pair in pairs_src:
                sum_src += probssrc[vocab[pair[0]]][vocab[pair[1]]]

            sum_trg = 0
            for pair in pairs_trg:
                sum_trg += probstrg[vocab[pair[0]]][vocab[pair[1]]]

            src_pow = sum_src_pow(pairs_src, vocab, probssrc)
            trg_pow = sum_src_pow(pairs_trg, vocab, probstrg)
        
        #if line_num > 99120 and line_num < 99130:
        #    flog.write(str(line_num) + ' error line\n')
       #    flog.write(str(len(alignments_src)) + '\n')
        #    flog.write(str(src_pow) + '\n')
       #     flog.write(str(sum_src) + 'sum_src \n')
       #     flog.write(str(math.pow(src_pow, 1/float(len(alignments_src)))) + '\n')
        
        alignments_sym = symmetrize_alignments_union(alignments_src, alignments_trg_normalized)
        if aligner == 'giza':
            features = [
            calculate_alignment(score_line_src, tokens_line_src.split()),
            calculate_alignment(score_line_trg, tokens_line_trg.split()),
            calculate_sym_ratio(alignments_sym, alignments_src),
            calculate_sym_ratio(alignments_sym, alignments_trg),
            0, 0, 0, 0, 0, 0, 0, 0
        ]
        elif aligner == 'fastalign':
            features = [
                0,
                0,
                calculate_sym_ratio(alignments_sym, alignments_src),
                calculate_sym_ratio(alignments_sym, alignments_trg),
                0 if len(alignments_src) == 0 else sum_src / len(alignments_src),
                0 if len(alignments_trg) == 0 else sum_trg / len(alignments_trg),
                0 if sum_src == 0 else math.log(abs(sum_src / len(alignments_src))),
                0 if sum_trg == 0 else math.log(abs(sum_trg / len(alignments_trg))),
                0 if sum_src == 0 else math.pow(src_pow, 1/float(len(alignments_src))),
                0 if sum_trg == 0 else math.pow(trg_pow, 1/float(len(alignments_trg))),
                0 if sum_src == 0 or src_pow == 0 else math.log(abs(math.pow(src_pow, 1/float(len(alignments_src))))),
                0 if sum_trg == 0 or trg_pow == 0 else math.log(abs(math.pow(trg_pow, 1/float(len(alignments_trg)))))
            ]
        features = map(lambda n: format_num(n, precision), features)
        
        if args.class_value: 
            features += [args.class_value]

        fout.write(delimiter.join(features) + '\n')

        line_num += 1
        if line_num % 100000 == 0:
            flog.write(str(line_num) + ' lines processsed\n')
        

    flog.write('Done, ' + str(line_num) + ' lines processed\n') 

    alssrc.close()
    alstrg.close()
    if aligner == 'fastalign':
        ctrg.close()
        csrc.close()
        tablesrc.close()
        tabletrg.close()

    fout.close()
    flog.close()