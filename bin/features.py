import sys
import os
import math
import argparse
from collections import defaultdict
import subprocess

# based on ca-align-1.1.1.py retrieved on 2014-06-30

def run(cmd, args):
    print 'Running ' + cmd + ' ' + ' '.join(args)
    proc = subprocess.Popen([cmd] + args)
    proc.wait()


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


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Extracts feature values from Giza++ output')
    parser.add_argument('-a', '--aligner', help='Aligner used or input type', choices=['giza', 'fastalign'], default='giza')
    parser.add_argument('-s', '--source-file', help='Source corpus file')
    parser.add_argument('-t', '--target-file', help='Target corpus file')
    parser.add_argument('-st', '--source-target-alignm', help='Src to trg file', required=True)
    parser.add_argument('-ts', '--target-source-alignm', help='Trg to src file', required=True)
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

    aligner = args.aligner if args.aligner != None else 'giza'
    delimiter = args.delimiter.replace('\\t', '\t') if args.delimiter != None else ','
    print_header = args.header.lower() != 'false' if args.header != None else True
    max_lines = int(args.lines) if args.lines != None else None
    precision = int(args.precision) if args.precision != None else 5

    columns = ['AlignmentScoreSource', 'AlignmentScoreTarget', 'SymRatioSource', 'SymRatioTarget', 'q', 'w', 'u', 'i', 'p', 'a', 'd', 'f',]

    if aligner == 'fastalign':
        # RUN pre-features.py:
        scriptPath = os.path.realpath(__file__)
        if not os.path.exists(args.source_file + '.probabilities.txt'):
            print "Running source pre-features"
            run('python', [scriptPath.replace('features.py', 'pre-features.py'), '-s', args.source_file, '-t', args.target_file, '-als', args.source_target_alignm, '-fa', args.fast_align_table_source, '-o', args.source_file])
        if not os.path.exists(args.target_file + '.probabilities.txt'):
            print "Running target pre-features"
            run('python', [scriptPath.replace('features.py', 'pre-features.py'), '-s', args.target_file, '-t', args.source_file, '-als', args.target_source_alignm, '-fa', args.fast_align_table_target, '-o', args.target_file])

        # Open files with probabilities
        probs_src_file = open(args.source_file + ".probabilities.txt", 'r')
        probs_trg_file = open(args.target_file + ".probabilities.txt", 'r')

        csrc = open(args.source_file, 'r')
        ctrg = open(args.target_file, 'r')

    if args.class_value: columns += ['class']
    line_num = 0

    if print_header:
        fout.write(delimiter.join(columns) + '\n')


    # Open Alignment files
    alssrc = open(args.source_target_alignm, 'r')
    alstrg = open(args.target_source_alignm, 'r')

    while max_lines == None or line_num < max_lines:
        if aligner == 'giza':
            score_line_src = alssrc.readline()
            score_line_trg = alstrg.readline()
            tokens_line_src = alssrc.readline()
            tokens_line_trg = alstrg.readline()
        #elif aligner == 'fastalign':
            #words_line_src = csrc.readline().split()
            #words_line_trg = ctrg.readline().split()

        alignments_line_src = alssrc.readline()
        alignments_line_trg = alstrg.readline()
        
        if not alignments_line_src or not alignments_line_trg:
            break
        
        if aligner == 'giza':
            alignments_src = extract_giza_alignments(alignments_line_src)
            alignments_trg = extract_giza_alignments(alignments_line_trg, reverse=True)
            alignments_sym = symmetrize_alignments_union(alignments_src, alignments_trg)
        elif aligner == 'fastalign':
            alignments_src = alignments_line_src.split()
            alignments_trg = alignments_line_trg.split()
            alignments_trg_normalized = extract_fastalign_alignments(alignments_line_trg, 'trg')

            probs_src_line = probs_src_file.readline()
            probs_trg_line = probs_trg_file.readline()
            probs_src = probs_src_line.split()
            probs_trg = probs_trg_line.split()

            sum_src = 0.0
            sum_trg = 0.0
            src_pow = 1.0
            trg_pow = 1.0

            for prob in probs_src:
                sum_src += float(prob)
                src_pow *= abs(float(prob))
            for prob in probs_trg:
                sum_trg += float(prob)
                trg_pow *= abs(float(prob))
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
                0 if sum_src == 0 or len(alignments_src) == 0 else math.log(abs(sum_src / len(alignments_src))),
                0 if sum_trg == 0 or len(alignments_trg) == 0 else math.log(abs(sum_trg / len(alignments_trg))),
                0 if sum_src == 0 or str(src_pow) == 'inf' or len(alignments_src) == 0 else math.pow(src_pow, 1/float(len(alignments_src))),
                0 if sum_trg == 0 or str(trg_pow) == 'inf' or len(alignments_trg) == 0 else math.pow(trg_pow, 1/float(len(alignments_trg))),
                0 if sum_src == 0 or src_pow == 0 or str(src_pow) == 'inf' or len(alignments_src) == 0 else math.log(abs(math.pow(src_pow, 1/float(len(alignments_src))))),
                0 if sum_trg == 0 or trg_pow == 0 or str(trg_pow) == 'inf' or len(alignments_trg) == 0 else math.log(abs(math.pow(trg_pow, 1/float(len(alignments_trg)))))
            ]
        features = map(lambda n: format_num(n, precision), features)
        
        if args.class_value: 
            features += [args.class_value]

        fout.write(delimiter.join(features) + '\n')

        #if 'inf' in features:
            #print src_pow, len(alignments_src), trg_pow, len(alignments_trg), 'line_num', str(line_num)          
        
        line_num += 1
        if line_num % 100000 == 0:
            flog.write(str(line_num) + ' lines processsed\n')
        

    flog.write('Done, ' + str(line_num) + ' lines processed\n') 

    alssrc.close()
    alstrg.close()
    if aligner == 'fastalign':
        ctrg.close()
        csrc.close()
    fout.close()
    flog.close()