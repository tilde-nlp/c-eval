import sys
import os
import argparse
import subprocess

def run(cmd, args, fout, ferr, flog):
    flog.write(' '.join([cmd] + args) + '\n\n')
    flog.flush()
    
    proc = subprocess.Popen([cmd] + args, stdout=fout, stderr=ferr)
    proc.wait()
    
    flog.write('\n\n')
    flog.flush()
    
def has_opt(kwargs, name):
    return name in kwargs and kwargs[name] != False
def default_opt(kwargs, name, default):
    return kwargs[name] if name in kwargs and kwargs[name] != None and kwargs[name] != False else default

def path(component, file):
    platform = 'windows' if os.name == 'nt' else 'linux'
    arch = 'x64'
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), platform, component, arch, file)
    
def remove(filename):
    if os.path.isfile(filename): 
        os.remove(filename)
def rename(old_filename, new_filename):
    remove(new_filename)
    os.rename(old_filename, new_filename)
    
def fastalign(src_filename, trg_filename, result_filename, log_file=None, args=None, **kwargs):
    # preprocess
    srctrg_filename = result_filename + '.combined'
    fastalign_create_inputfile(src_filename, trg_filename, srctrg_filename, ' ||| ')
    
    # arguments
    if args == None: args = ['-d', '-o', '-v']
    if has_opt(kwargs, 'keep_table'): args += ['-c', default_opt(kwargs, 'keep_table', result_filename + '.fastalign.table')]
    args += ['-i', srctrg_filename]
    
    # execute
    fout = open(result_filename, 'w')
    run(path('fastalign', 'fast_align'), args, fout, log_file, log_file)
    fout.close()
    
    if has_opt(kwargs, 'keep_input'):
        rename(srctrg_filename, default_opt(kwargs, 'keep_input', result_filename + '.fastalign.input'))
    else:
        remove(srctrg_filename)
        
def fastalign_create_inputfile(src_filename, trg_filename, out_filename, separator=' ||| '):
    fsrc = open(src_filename, 'r')
    ftrg = open(trg_filename, 'r')
    fout = open(out_filename, 'w')
    while True:
        src_line = fsrc.readline().rstrip()
        trg_line = ftrg.readline().rstrip()
        if not src_line or not trg_line: break
        fout.write(src_line + separator + trg_line + '\n')
    fout.close()
    fsrc.close()
    ftrg.close()

def giza(src_filename, trg_filename, result_filename, log_file=None, giza_args=None, **kwargs):
    # giza tools remove .txt and .tok file extension and create intermediate files using the file name without extension
    src_basefilename, src_ext = os.path.splitext(os.path.basename(src_filename))
    trg_basefilename, trg_ext = os.path.splitext(os.path.basename(trg_filename))
    if not src_ext.lower() in ['.txt', '.tok']: src_basefilename = src_filename
    if not trg_ext.lower() in ['.txt', '.tok']: trg_basefilename = trg_filename
    src_trg = src_basefilename + '_' + trg_basefilename
    trg_src = trg_basefilename + '_' + src_basefilename
    src_vcb = src_basefilename + '.vcb'
    trg_vcb = trg_basefilename + '.vcb'
    src_trg_snt = src_trg + '.snt'
    trg_src_snt = trg_src + '.snt'
    cooc = src_trg + '.cooc'
    gizabase = src_trg + '.giza'
    gizabase_cfg = gizabase + '.gizacfg'
    gizabase_out = gizabase + '.A3.final'
    
    # creates srcbase.vcb trgbase.vcb srcbase_trgbase.snt trgbase_srcbase.snt
    run(path('giza', 'plain2snt'), [src_filename, trg_filename], log_file, log_file, log_file)
    # creates srcbase.vcb.classes srcbase.vcb.classes.cats
    run(path('giza', 'mkcls'), ['-p' + src_filename, '-V' + src_vcb + '.classes'], log_file, log_file, log_file)
    # creates trgbase.vcb.classes trgbase.vcb.classes.cats
    run(path('giza', 'mkcls'), ['-p' + trg_filename, '-V' + trg_vcb + '.classes'], log_file, log_file, log_file)
    # cooccurence file
    cooc_file = open(cooc, 'w')
    run(path('giza', 'snt2cooc'), [src_vcb, trg_vcb, src_trg_snt], cooc_file, log_file, log_file)
    cooc_file.close()

    # arguments
    if giza_args == None: 
        giza_args = '-m1 5 -m2 0 -m3 3 -m4 3 -model1dumpfrequency 1 -model4smoothfactor 0.4 -nodumps 1 -nsmooth 4 -onlyaldumps 1 -p0 0.999'.split()
    giza_args += ['-s', src_vcb]
    giza_args += ['-t', trg_vcb]
    giza_args += ['-c', src_trg_snt]
    giza_args += ['-CoocurrenceFile', cooc]
    giza_args += ['-o', gizabase]
    
    # execute
    run(path('giza', 'gizapp'), giza_args, log_file, log_file, log_file)
    # postprocess
    giza_convert_alignments(gizabase_out, result_filename)
    
    if not has_opt(kwargs, 'keep_extra'):
        remove(src_vcb)
        remove(trg_vcb)
        remove(src_vcb + '.classes')
        remove(trg_vcb + '.classes')
        remove(src_vcb + '.classes.cats')
        remove(trg_vcb + '.classes.cats')
        remove(src_trg_snt)
        remove(trg_src_snt)
        remove(cooc)
    
    if has_opt(kwargs, 'keep_cfg'):
        rename(gizabase_cfg, default_opt(kwargs, 'keep_cfg', result_filename + '.gizacfg'))
    else:
        remove(gizabase_cfg)
        
    if has_opt(kwargs, 'keep_output'):
        rename(gizabase_out, default_opt(kwargs, 'keep_output', result_filename + '.giza'))
    else:
        remove(gizabase_out)

def giza_convert_alignments(input_filename, output_filename):
    fin = open(input_filename, 'r')
    fout = open(output_filename, 'w')
    while True:
        score_line = fin.readline()
        if not score_line: break
        tokens_line = fin.readline()
        alignments_line = fin.readline()
        alignments = giza_convert_alignments_line(alignments_line)
        fout.write(' '.join(alignments) + '\n')
    fin.close()
    fout.close()
    
def giza_convert_alignments_line(line, reverse=False):
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

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Creates word alignments from parallel corpora')
    parser.add_argument('-a', '--aligner', help='Aligner to use', required=True, choices=['giza', 'fastalign'])
    parser.add_argument('-x', '--aligner-args', help='Arguments for aligner')
    parser.add_argument('-s', '--source-file', help='Source corpus file', required=True)
    parser.add_argument('-t', '--target-file', help='Target corpus file', required=True)
    parser.add_argument('-st', '--source-target-file', help='Output file for source-target word alignments')
    parser.add_argument('-ts', '--target-source-file', help='Output file for target-source word alignments')
    parser.add_argument('-l', '--log-file', help='Log file')
    parser.add_argument('-k', '--keep-extra', help='Keep generated intermediate files', action='store_true', default=False)
    parser.add_argument('--giza-keep-output', help='Keep GIZA++ output file', nargs='?', default=None)
    parser.add_argument('--giza-keep-cfg', help='Keep GIZA++ configuration file', nargs='?', default=False)
    parser.add_argument('--fastalign-keep-input', help='Keep fastalign input file (both corpora in one file)', nargs='?', default=False)
    parser.add_argument('--fastalign-keep-table', help='Keep fastalign conditional table', nargs='?', default=False)
    args = parser.parse_args()
    
    flog = open(args.log_file, 'w') if args.log_file else sys.stdout
    
    if args.aligner == 'giza':
        
        if args.source_target_file:
            giza(args.source_file, args.target_file, args.source_target_file, flog, args.aligner_args, 
                 keep_extra=args.keep_extra,
                 keep_cfg=args.giza_keep_cfg,
                 keep_output=args.giza_keep_output)
         
        if args.target_source_file:
            giza(args.target_file, args.source_file, args.target_source_file, flog, args.aligner_args, 
                 keep_extra=args.keep_extra,
                 keep_cfg=args.giza_keep_cfg,
                 keep_output=args.giza_keep_output)
             
    elif args.aligner == 'fastalign':
        
        if args.source_target_file:
            fastalign(args.source_file, args.target_file, args.source_target_file, flog, args.aligner_args,
                      keep_input=args.fastalign_keep_input,
                      keep_table=args.fastalign_keep_table)
                      
        if args.target_source_file:
            fastalign(args.target_file, args.source_file, args.target_source_file, flog, args.aligner_args,
                      keep_input=args.fastalign_keep_input,
                      keep_table=args.fastalign_keep_table)
    
    flog.close()
