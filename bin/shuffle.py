import argparse
import random

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Shuffles lines in a file')
    parser.add_argument('-i', '--input-file', help='Input file', required=True)
    parser.add_argument('-o', '--output-file', help='Shuffled output file', required=True)
    args = parser.parse_args()

    with open(args.input_file, 'r') as fin:
        lines = fin.readlines()
        
    random.shuffle(lines)

    with open(args.output_file, 'w') as fout:
        fout.writelines(lines)
