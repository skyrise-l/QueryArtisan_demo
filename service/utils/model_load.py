# utils/model_loader.py

import torch
from transformers import BertTokenizer, BertModel
from transformers import pipeline

class BertModelLoader:
    def __init__(self):
        self.tokenizer = None
        self.model = None
        self.nlp_model = None

    def load_model(self):
        """加载BERT模型和分词器，并保持在内存中"""
        if self.tokenizer is None or self.model is None:
            print("Loading BERT model...")
            self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
            self.model = BertModel.from_pretrained('bert-base-uncased')

            self.nlp_model = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english")
        else:
            print("BERT model already loaded.")
    
    def get_model(self):
        """返回加载的BERT模型"""
        return self.model
    
    def get_tokenizer(self):
        """返回BERT分词器"""
        return self.tokenizer

    def get_nlp_model(self):
        """返回BERT分词器"""
        return self.nlp_model

