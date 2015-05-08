# C-Eval - paralllel corpora cleaning and evaluation tool

C-Eval presents a method for cleaning and evaluating parallel corpora using word alignments and machine learning algorithms. It is based on the assumption that parallel sentences have many word alignments while non-parallel sentences have few or none. We show that it is possible to build an automatic classifier, which identifies most of non-parallel sentences in a parallel corpus. This method allows us to do (1) automatic quality evaluation of parallel corpus and (2) automatic parallel corpus cleaning. The method allows us to get cleaner parallel corpora, smaller statistical models, and faster MT training, but this does not always guarantee higher BLEU scores.

## Requirements

* Linux or Windows
* PyPy 2.5.1
* Java 7 or 8
* [Visual C++ Redistributable Packages](https://www.microsoft.com/en-us/download/details.aspx?id=40784) on Windows

We use [fast align](https://github.com/clab/fast_align) for word alignment and [Weka](http://www.cs.waikato.ac.nz/ml/weka/) for machine learning.

## Training

First, you need to train a model on a good parallel corpus.

Run:

```bash
pypy cleaner.py                   \
  -train                          \
  -s corpus.en -t corpus.fr       \
  -a fastalign -c reptree         \
  -m corpus.en-fr.fastalign.reptree.model
```

Arguments:

* `-train` - perform training
* `-s <source corpus>` - source corpus
* `-t <target corpus>` - target corpus
* `-a <aligner>` - word aligner, always `fastalign`
* `-c <classifier>` - classifier (machine learning algorithm): `extratrees`, `j48` or `reptree`
* `-m <model filename>` - output filename for the trained model

## Cleaning

Run:

```bash
pypy cleaner.py                                \
    -s othercorpus.en -t othercorpus.fr        \  
    -a fastalign -m corpus.en-fr.fastalign.reptree.model
```

Arguments:

* `-s <source corpus>` - source corpus
* `-t <target corpus>` - target corpus
* `-a <aligner>` - word aligner, always `fastalign`
* `-m <model filename>` previously trained model

The script has to be run from the corpus directory. The output files will be produced in the corpus folder named as `<source corpus>.filtered` and `<target corpus>.filtered`, e.g.,`othercorpus.en.filtered.txt`, and `othercorpus.en.filtered.BAD.txt`
