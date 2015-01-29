package com.tilde.corpora.cleaner;

import java.io.BufferedWriter;
import java.io.FileOutputStream;
import java.io.OutputStreamWriter;
import java.util.HashMap;
import java.util.Map;
import java.util.Random;

import com.beust.jcommander.JCommander;
import com.beust.jcommander.Parameter;
import com.beust.jcommander.ParameterException;

import weka.core.Instances;
import weka.classifiers.Classifier;
import weka.classifiers.Evaluation;
import weka.classifiers.trees.ExtraTree;
import weka.classifiers.trees.J48;
import weka.classifiers.trees.REPTree;

public class Main {
	public static void main(String[] args) throws Exception {
		// -train -m model.bin -f features.txt [ -e efeatures.txt ] 
		// -m model.bin -f features.txt -s src.txt -t trg.txt -os src.f.txt -ot trg.f.txt
		int good = 0;
		int bad = 0;
		Options options = new Options();
		JCommander cmd = new JCommander(options);
		try {
			cmd.parse(args);
			
			if (options.help) {
				cmd.usage();
				return;
			}
		} catch (ParameterException e) {
			System.err.println(e.getMessage() + "\n");
			StringBuilder sb = new StringBuilder();
			cmd.usage(sb);
			System.err.print(sb.toString());
			return;
		} 
		
		if (options.train) {
			Loader loader = new Loader(options.inputFeaturesFilename);
			Instances instances = loader.getAll();
			loader.close();
			
			Classifier classifier = getClassifiers().get(options.classifierName.toLowerCase());
			classifier.buildClassifier(instances);
			weka.core.SerializationHelper.write(options.modelFilename, classifier);
			
			if (options.evaluationFeaturesFilename != null) {
				Loader evaluationLoader = new Loader(options.evaluationFeaturesFilename);
				Instances evaluationInstances = evaluationLoader.getAll();
				evaluationLoader.close();
				
				Evaluation evaluation = new Evaluation(evaluationInstances);
				evaluation.crossValidateModel(classifier, evaluationInstances, 10, new Random(1));
				System.out.println(evaluation.toSummaryString("Results\n=======\n", false));
			}
		} else {
			Classifier classifier = (Classifier) weka.core.SerializationHelper.read(options.modelFilename);
			
			Loader loader = new Loader(options.inputFeaturesFilename, options.inputSourceSentencesFilename, options.inputTargetSentencesFilename);
			
			BufferedWriter sourceSentenceWriter = new BufferedWriter(new OutputStreamWriter(new FileOutputStream(options.outputSourceSentencesFilename), "UTF-8"));
			BufferedWriter targetSentenceWriter = new BufferedWriter(new OutputStreamWriter(new FileOutputStream(options.outputTargetSentencesFilename), "UTF-8"));
			
			while (!loader.isEnd()) {
				SentenceInstance instance = loader.getNext();
				instance.setClassValue(classifier.classifyInstance(instance));
				
				if (instance.isGoodSentence()) {
					sourceSentenceWriter.write(instance.getSourceSentence() + "\n");
					targetSentenceWriter.write(instance.getTargetSentence() + "\n");
					good += 1; 
				} else {
					bad += 1;
				}
			}
			
			sourceSentenceWriter.close();
			targetSentenceWriter.close();
			
			loader.close();
			
			System.out.println("good = " + good);
			System.out.println("bad = " + bad);
			System.out.println((100.*good/(bad + good)) + "% of good sentences");
			System.out.println((100.*bad/(bad + good)) + "% of bad sentences");
		}		
	}

	public static Map<String, Classifier> getClassifiers() {
		HashMap<String, Classifier> classifiers = new HashMap<String, Classifier>();
		classifiers.put("j48", new J48());
		classifiers.put("extratrees", new ExtraTree());
		classifiers.put("extratree", new ExtraTree());
		classifiers.put("reptree", new REPTree());
		return classifiers;
	}
	
	public static class Options {
		@Parameter(names = "-train", description = "Train model")
	    public boolean train;
		@Parameter(names = { "-c", "-classifier", "--classifier" }, description = "Classification algorithm to use")
	    public String classifierName;
	    @Parameter(names = { "-m", "-model", "--model" }, description = "Path to model file", required = true)
	    public String modelFilename;
	    @Parameter(names = { "-e", "-eval", "--eval" }, description = "Path to features file for 10-fold cross-validation")
	    public String evaluationFeaturesFilename;
	    @Parameter(names = { "-f", "-features", "--features" }, description = "Path to features file", required = true)
	    public String inputFeaturesFilename;
	    @Parameter(names = { "-s", "-is", "-src", "--src", "--src-input" }, description = "Path to sentences in source language")
	    public String inputSourceSentencesFilename;
	    @Parameter(names = { "-t", "-it", "-trg", "--trg", "--trg-input" }, description = "Path to sentences in target language")
	    public String inputTargetSentencesFilename;
	    @Parameter(names = { "-os", "-osrc", "--src-output" }, description = "Path for saving filtered sentences in source language")
	    public String outputSourceSentencesFilename;
	    @Parameter(names = { "-ot", "-otrg", "--trg-output" }, description = "Path for saving filtered sentences in target language")
	    public String outputTargetSentencesFilename;
	    @Parameter(names = { "-h", "-help", "--help" }, help = true)
	    public boolean help;
	}
}
