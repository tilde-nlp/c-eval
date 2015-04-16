# c-eval
Paralllel corpora cleaning and evaluation tool

This tool C-Eval presents a method for cleaning and evaluating parallel corpora using word alignments and machine learning algorithms. It is based on the assumption that parallel sentences have many word alignments while non-parallel sentences have few or none. We show that it is possible to build an automatic classifier, which identifies most of non-parallel sentences in a parallel corpus. This method allows us to do (1) automatic quality evaluation of parallel corpus and (2) automatic parallel corpus cleaning. The method allows us to get cleaner parallel corpora, smaller statistical models, and faster MT training, but this does not always guarantee higher BLEU scores.

