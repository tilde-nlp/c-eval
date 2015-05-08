package com.tilde.corpora.cleaner;

import weka.core.DenseInstance;

public class SentenceInstance extends DenseInstance {
	private static final long serialVersionUID = 2256225032530928966L;
	
	public static final double GOOD = 1;
	public static final double BAD = 0;
	
	private String sourceSentence;
	private String targetSentence;

	public SentenceInstance(int size) {
		super(size);
	}
	
	public String getSourceSentence() {
		return sourceSentence;
	}
	
	public void setSourceSentence(String sourceSentence) {
		this.sourceSentence = sourceSentence;
	}
	
	public String getTargetSentence() {
		return targetSentence;
	}
	
	public void setTargetSentence(String targetSentence) {
		this.targetSentence = targetSentence;
	}
	
	public boolean isGoodSentence() {
		return classValue() == GOOD;
	}
}
