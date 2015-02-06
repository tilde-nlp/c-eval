# Corpus Cleaner

`cleaner.py` is a script for parallel corpus cleaning based on machine leanrning. It incorperates WEKA library as well as Fastalign and Giza++ aligners. The cleaner outputs respective parallel corpus of filtered (good) sentences that have been judjed as good by the model. The model should be trained on a corpus that is known to contain good, parallel trainslations. For more accurate results the same language pair should be used for both the model and the parallel corpus that is to be cleaned.

# Model training process:
The statistical machine leanrning model requires "good" and "bad" data input for comparison. "Good" data is taken from the source corpus, while "bad" data is generated form the target corpus by shiffling the lines.

Training of "good" lines includes:
  * "Good" corpus alignment by Giza++ or Fastalign, generating alignment files.
  * Feature generation form the alignments.
 
Training of "bad" lines includes:
  * Shuffling lines of target corpus.
  * "Bad" corpus alignment by Giza++ or Fastalign, generating alignment files.
  * Feature generation form the alignments.
  
"good"  + "bad"
  * Merging "good" and "bad" features into one file
  * Training the model with WEKA library.

Example:

    python cleaner.py -train
		      -s en.100k.txt 
		      -t lv.100k.txt 
		      -a giza 
		      -c reptree 
		      -m en-lv.10k.giza.reptree.model

`-train` signals model training, `-s <source_corpus>` - source corpus, `-t <target_corpus>`- target courpus, `-a <aligner>` - aligner (alignment program) in this case either `giza` or `fastalign`, `-c <classifier>` - classifier (machine learning algorithm either `extratrees`, `j48` or `reptree`), `-m <model_name>` - the neme of the trained model.

# Corpus cleaning:
  * Corpus alignment by Giza++ or Fastalign, generating alignment files.
  * Filtering lines according to the generated features and given model.

Example:

	python cleaner.py -a giza 
			  -s en.10k.txt 
			  -t lv.10k.txt 
			  -m en-lv.100k.giza.reptree.model
`-m <model>` - previously trained model 

The script should be run from the corpus directory. The output files will be produced in the corpus folder named as `<source_corpus_name>.filtered` and `<target_corpus_name>.filtered`, e.g.,  `en.10K.txt.filtered.txt` and `lv.10K.txt.filtered.txt`