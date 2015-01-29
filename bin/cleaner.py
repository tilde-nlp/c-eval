#python clean.py --train -s en.txt -t lv.txt -a giza -m modelis.extratrees.bin -c extratrees
import sys
import os
import argparse
import subprocess


def run(cmd, args):
    print 'Running ' + cmd + ' ' + ' '.join(args)
    proc = subprocess.Popen([cmd] + args)
    proc.wait()


def rename(old_filename, new_filename):
    if os.path.exists(new_filename): os.remove(new_filename)
    os.rename(old_filename, new_filename)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Filters corpus based on a trained model')
    parser.add_argument('-train', help='Training mode for training a model')
    parser.add_argument('-a', '--aligner', help='Aligner to use', choices=['giza', 'fastalign'])
    parser.add_argument('-x', '--aligner-args', help='Arguments for aligner')
    parser.add_argument('-s', '--source-file', help='Source corpus file')
    parser.add_argument('-t', '--target-file', help='Target corpus file')
    parser.add_argument('-st', '--source-target-file', help='Output file for source-target alignments')
    parser.add_argument('-ts', '--target-source-file', help='Output file for target-source alignments')
    parser.add_argument('-m', '--model', help='Model for filtering sentences')
    parser.add_argument('-f', '--features-file', help='Features of the corpus to clean')
    parser.add_argument('-o', '--output-file', help='Features output file')
    parser.add_argument('-p', '--precision', help='Floating number precision', type=int)
    parser.add_argument('-n', '--lines', help='Number of sentences to process', type=int)
    parser.add_argument('-d', '--delimiter', help='Delimiter')
    parser.add_argument('-c', '--classifier', help='Classifier algorithm')
    parser.add_argument('-e', '--evaluation', help='Cross-evaluation for model')
    parser.add_argument('-l', '--log-file', help='Log file')
    parser.add_argument('-k', '--keep-extra', help='Keep generated intermediate files', action='store_true', default=False)
    parser.add_argument('--giza-keep-output', help='Keep GIZA++ output file', nargs='?', default=None)
    parser.add_argument('--giza-keep-cfg', help='Keep GIZA++ configuration file', nargs='?', default=False)
    parser.add_argument('--fastalign-keep-input', help='Keep fastalign input file (both corpora in one file)', nargs='?',default=False)
    parser.add_argument('--fastalign-keep-table', help='Keep fastalign conditional table', nargs='?', default=False)
    parser.add_argument('-fas', '--fast-align-table-source', help='Fast-align table for source alignments')
    parser.add_argument('-fat', '--fast-align-table-target', help='Fast-align table for target alignments')

    args = parser.parse_args()

    flog = open(args.log_file, 'w') if args.log_file else sys.stdout

    scriptPath = os.path.realpath(__file__)

    if args.train:
        #trenne ar aligner
        args.source_target_file = 'cleaner-train.src-trg.good.alignments-' + args.source_file
        args.target_source_file = 'cleaner-train.trg-src.good.alignments-' + args.target_file
        if not os.path.exists(args.source_target_file):
            run('python', [scriptPath.replace("cleaner.py", 'aligner/aligner.py'), '-a', args.aligner, '-s', args.source_file, '-t', args.target_file, '-st', args.source_target_file, '--giza-keep-output', '--fastalign-keep-table'])
            if args.aligner == 'giza': rename(args.source_target_file + '.giza', args.source_target_file)
        if not os.path.exists(args.target_source_file):
            run('python', [scriptPath.replace("cleaner.py", 'aligner/aligner.py'), '-a', args.aligner, '-s', args.source_file, '-t', args.target_file, '-ts', args.target_source_file, '--giza-keep-output','--fastalign-keep-table'])
            if args.aligner == 'giza': rename(args.target_source_file + '.giza', args.target_source_file)

        #uztaisa sliktos datus modela testesanai/trenesanai
        if not os.path.exists('cleaner-train.trg.bad.' + args.target_file):
            run('python', [scriptPath.replace("cleaner.py", 'shuffle.py'), '-i', args.target_file, '-o', 'cleaner-train.trg.bad-' + args.target_file])

        args.source_target_file = 'cleaner-train.src-trg.bad.alignments-' + args.source_file
        args.target_source_file = 'cleaner-train.trg-src.bad.alignments-' + args.target_file
        #trenne ar aligner bad datus
        if not os.path.exists(args.source_target_file):
            run('python', [scriptPath.replace("cleaner.py", 'aligner/aligner.py'), '-a', args.aligner, '-s', args.source_file, '-t', 'cleaner-train.trg.bad-' + args.target_file, '-st', args.source_target_file, '--giza-keep-output', '--fastalign-keep-table'])
            if args.aligner == 'giza': rename(args.source_target_file + '.giza', args.source_target_file)
        if not os.path.exists(args.target_source_file):
            run('python', [scriptPath.replace("cleaner.py", 'aligner/aligner.py'), '-a', args.aligner, '-s', args.source_file, '-t', 'cleaner-train.trg.bad-' + args.target_file, '-ts', args.target_source_file, '--giza-keep-output', '--fastalign-keep-table'])
            if args.aligner == 'giza': rename(args.target_source_file + '.giza', args.target_source_file)

        #izvelk features ara no good/bad teikumiem
        args.features_file = 'cleaner-train.features-' + args.source_file + '.' + args.target_file
        if not os.path.exists(args.features_file):
            if args.aligner == 'giza':
                run('python', [scriptPath.replace('cleaner.py', 'features.py'), '-a', args.aligner, '-st', 'cleaner-train.src-trg.good.alignments-' + args.source_file, '-ts', 'cleaner-train.trg-src.good.alignments-' + args.target_file, '-o', 'cleaner-train.features.good.txt', '-c', 'good', '-p', '8'])
                run('python', [scriptPath.replace('cleaner.py', 'features.py'), '-a', args.aligner, '-st', 'cleaner-train.src-trg.bad.alignments-' + args.source_file, '-ts', 'cleaner-train.trg-src.bad.alignments-' + args.target_file, '-o', 'cleaner-train.features.bad.txt', '-c', 'bad', '-p', '8'])
            if args.aligner == 'fastalign':
                run('python', [scriptPath.replace('cleaner.py', 'features.py'), '-a', args.aligner, '-s', args.source_file, '-t', args.target_file, '-st', 'cleaner-train.src-trg.good.alignments-' + args.source_file, '-ts', 'cleaner-train.trg-src.good.alignments-' + args.target_file,'-fas', 'cleaner-train.src-trg.good.alignments-' + args.source_file + '.fastalign.table' , '-fat', 'cleaner-train.trg-src.good.alignments-' + args.target_file + '.fastalign.table','-o', 'cleaner-train.features.good.txt', '-c', 'good', '-p', '8'])
                run('python', [scriptPath.replace('cleaner.py', 'features.py'), '-a', args.aligner, '-s', args.source_file, '-t', 'cleaner-train.trg.bad-' + args.target_file,'-st', 'cleaner-train.src-trg.bad.alignments-' + args.source_file, '-fas', 'cleaner-train.src-trg.bad.alignments-' + args.source_file + '.fastalign.table' , '-fat', 'cleaner-train.trg-src.bad.alignments-' + args.target_file + '.fastalign.table','-ts', 'cleaner-train.trg-src.bad.alignments-' + args.target_file, '-o', 'cleaner-train.features.bad.txt', '-c', 'bad', '-p', '8'])

            #saliek kopa good + bad = cleaner-train.features.txt
            fg = open ('cleaner-train.features.good.txt', 'r')
            fb = open('cleaner-train.features.bad.txt', 'r')
            f = open(args.features_file, 'w')

            for line in fg:
                f.write(line.rstrip() + '\n')
            fb.readline()
            for line in fb:
                f.write(line.rstrip() + '\n')
            fg.close()
            fb.close()
            os.remove('cleaner-train.features.good.txt')
            os.remove('cleaner-train.features.bad.txt')
            f.close()

        #uztaisa modeli
        if not os.path.exists(args.model):
            if args.evaluation:
                run('java', ['-jar', scriptPath.replace('cleaner.py', 'classifier.jar'), '-train', '-c', args.classifier,'-m', args.model, '-f', args.features_file, '-e', args.evaluation])
            else:
                run('java', ['-jar', scriptPath.replace('cleaner.py', 'classifier.jar'), '-train', '-c', args.classifier,'-m', args.model, '-f', args.features_file])
    else:
        args.source_target_file = 'cleaner.src-trg.alignments-' + args.source_file
        args.target_source_file = 'cleaner.trg-src.alignments-' + args.target_file
        args.features_file = 'cleaner-test.features-' + args.source_file + '.' + args.target_file
        args.output_file = args.features_file

        if not os.path.exists(args.source_target_file):
            run('python', [scriptPath.replace('cleaner.py', 'aligner/aligner.py'), '-a', args.aligner, '-s', args.source_file, '-t', args.target_file, '-st', args.source_target_file, '--giza-keep-output', '--fastalign-keep-table'])
            if args.aligner == 'giza':
                rename(args.source_target_file + '.giza', args.source_target_file)
        if not os.path.exists(args.target_source_file):
            run('python', [scriptPath.replace('cleaner.py', 'aligner/aligner.py'), '-a', args.aligner, '-s', args.source_file, '-t', args.target_file, '-ts', args.target_source_file, '--giza-keep-output', '--fastalign-keep-table'])
            if args.aligner == 'giza': rename(args.target_source_file + '.giza', args.target_source_file)
        #izvelk features ara, ja nav tada faila jau gatava
        if not os.path.exists(args.features_file):
            if args.aligner == 'giza': run('python', [scriptPath.replace('cleaner.py', 'features.py'), '-a', args.aligner, '-st', args.source_target_file, '-ts', args.target_source_file, '-o', args.output_file , '-p', '8'])
            elif args.aligner == 'fastalign': run('python', [scriptPath.replace('cleaner.py', 'features.py'), '-a', args.aligner, '-s', args.source_file, '-t', args.target_file, '-st', args.source_target_file, '-ts', args.target_source_file,'-fas', args.source_target_file +  '.fastalign.table' , '-fat', args.target_source_file + '.fastalign.table','-o', args.output_file, '-p', '8'])

        #palaiz atlasi, ja padod modela argumetu
        if args.model:
            run('java', ['-jar', scriptPath.replace('cleaner.py', 'classifier.jar'), '-m', args.model, '-f', args.features_file, '-s', args.source_file, '-t', args.target_file, '-os', args.source_file + '.filtered.txt', '-ot', args.target_file + '.filtered.txt'])
