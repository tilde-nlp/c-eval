package com.tilde.corpora.cleaner;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Arrays;

import weka.core.Attribute;
import weka.core.Instances;

public class Loader {
	public static final String GOOD = "good";
	public static final String BAD = "bad";
	public static final String CLASS_COLUMN = "class";
	
	private BufferedReader featuresReader, sourceSentencesReader, targetSentencesReader;
	private String delimiter = ",";
	
	private ArrayList<Attribute> attributes = new ArrayList<Attribute>();
	private int classAttributeIndex =- 1;
	
	public Loader(String featuresFilename) throws Exception {
		featuresReader = new BufferedReader(new InputStreamReader(new FileInputStream(featuresFilename), "UTF-8"));
		
		// generate attributes from header
		String headerLine = featuresReader.readLine();
		String[] columns = headerLine.split(getDelimiter());
		for (int i = 0; i < columns.length; i++) {
			if (columns[i].equalsIgnoreCase(CLASS_COLUMN)) {
				attributes.add(new Attribute(columns[i], Arrays.asList(new String[] { GOOD, BAD })));
				classAttributeIndex = i;
			} else {
				attributes.add(new Attribute(columns[i]));				
			}
		}
		// no class column, it means it's unlabeled data for classification
		// add it because it must exist
		if (classAttributeIndex == -1) {
			attributes.add(new Attribute(CLASS_COLUMN, Arrays.asList(new String[] { GOOD, BAD })));
			classAttributeIndex = attributes.size() - 1;
		}
	}
	
	public Loader(String featuresFilename, String sourceSentencesFilename, String targetSentencesFilename) throws Exception {
		this(featuresFilename);
		sourceSentencesReader = new BufferedReader(new InputStreamReader(new FileInputStream(sourceSentencesFilename), "UTF-8"));
		targetSentencesReader = new BufferedReader(new InputStreamReader(new FileInputStream(targetSentencesFilename), "UTF-8"));
	}
	
	public String getDelimiter() {
		return delimiter;
	}

	public void setDelimiter(String delimiter) {
		this.delimiter = delimiter;
	}

	public Instances getStructure() {
		Instances structure = new Instances("Sentence", attributes, attributes.size());
		structure.setClassIndex(classAttributeIndex);
		return structure;
	}
	
	public Instances getAll() {
		Instances instances = getStructure();
		while (!isEnd()) {
			instances.add(getNext());
		}
		return instances;
	}
	
	public SentenceInstance getNext() {
		try {
			SentenceInstance instance = new SentenceInstance(attributes.size());
			instance.setDataset(getStructure());
			instance.setClassMissing();
			if (sourceSentencesReader != null) instance.setSourceSentence(sourceSentencesReader.readLine());
			if (targetSentencesReader != null) instance.setTargetSentence(targetSentencesReader.readLine());
			
			String features = featuresReader.readLine();
			String[] values = features.split(getDelimiter());
			for (int i = 0; i < values.length; i++) {
				if (i == classAttributeIndex && (values[i].equals(GOOD) || values[i].equals(BAD))) {
					instance.setClassValue(values[i].equals(GOOD) ? SentenceInstance.GOOD : SentenceInstance.BAD);
				} else if (!values[i].isEmpty()) {
					instance.setValue(i, Float.parseFloat(values[i]));
				}
			}
			
			return instance;
		} catch (Exception e) {
			e.printStackTrace();
			return null;
		}
	}
	
	public boolean isEnd() {
		try {
			return !featuresReader.ready();
		} catch (IOException e) {
			return true;
		}
	}
	
	public void close() {
		try {
			featuresReader.close();
			if (sourceSentencesReader != null) sourceSentencesReader.close();
			if (targetSentencesReader != null) targetSentencesReader.close();
		} catch (IOException e) {
			return;
		}
	}
}
